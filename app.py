#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación web para procesar códigos EAN usando GO-UPC API
Interfaz de usuario para cargar archivos .txt y descargar Excel procesado
"""

import os
import tempfile
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from goupc_automation import (
    leer_codigos_desde_archivo,
    procesar_codigos_con_reintentos,
    guardar_excel_goupc,
    guardar_json
)

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui_2024'

# Configuración de archivos
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max

# Crear directorio de uploads si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('temp', exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    """Verificar si el archivo tiene extensión permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Procesar archivo subido"""
    try:
        # Verificar si se subió un archivo
        if 'file' not in request.files:
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
        file = request.files['file']
        
        # Verificar si se seleccionó un archivo
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
        # Verificar extensión
        if not allowed_file(file.filename):
            return jsonify({'error': 'Solo se permiten archivos .txt'}), 400
        
        # Guardar archivo temporalmente
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # Leer códigos del archivo
        codigos = leer_codigos_desde_archivo(filepath)
        
        if not codigos:
            os.remove(filepath)  # Limpiar archivo temporal
            return jsonify({'error': 'No se encontraron códigos válidos en el archivo'}), 400
        
        # Procesar códigos
        resultados = procesar_codigos_con_reintentos(codigos)
        
        if not resultados:
            os.remove(filepath)  # Limpiar archivo temporal
            return jsonify({'error': 'No se obtuvieron resultados del procesamiento'}), 400
        
        # Generar archivos de salida
        excel_filename = f"productos_goupc_{timestamp}.xlsx"
        json_filename = f"productos_goupc_{timestamp}.json"
        
        excel_path = os.path.join('temp', excel_filename)
        json_path = os.path.join('temp', json_filename)
        
        # Guardar Excel y JSON
        guardar_excel_goupc(resultados, excel_path)
        guardar_json(resultados, json_path)
        
        # Calcular estadísticas
        encontrados = len([r for r in resultados if r.get('producto_encontrado')])
        errores = len([r for r in resultados if r.get('error')])
        completados_ia = len([r for r in resultados if r.get('datos_completados_ia')])
        
        # Limpiar archivo temporal
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': 'Procesamiento completado exitosamente',
            'stats': {
                'total_procesados': len(resultados),
                'encontrados': encontrados,
                'errores': errores,
                'completados_ia': completados_ia,
                'tasa_exito': round((encontrados/len(resultados)*100), 1)
            },
            'files': {
                'excel': excel_filename,
                'json': json_filename
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Error durante el procesamiento: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Descargar archivo procesado"""
    try:
        file_path = os.path.join('temp', filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Archivo no encontrado'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        return jsonify({'error': f'Error al descargar archivo: {str(e)}'}), 500

@app.route('/cleanup', methods=['POST'])
def cleanup_files():
    """Limpiar archivos temporales"""
    try:
        temp_dir = 'temp'
        if os.path.exists(temp_dir):
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        
        return jsonify({'success': True, 'message': 'Archivos temporales limpiados'})
        
    except Exception as e:
        return jsonify({'error': f'Error al limpiar archivos: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Iniciando aplicación web para procesamiento de EAN...")
    print("📱 Abre tu navegador en: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

# Para Vercel
app.debug = False 