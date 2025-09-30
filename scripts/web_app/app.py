from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import os
import json
import requests
from datetime import datetime
from PIL import Image
from io import BytesIO
import base64
import openpyxl
from openpyxl import Workbook
from dotenv import load_dotenv
import tempfile
import shutil

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

# Configuración de directorios
UPLOAD_FOLDER = 'static/uploads'
PROCESSED_FOLDER = 'static/processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def get_product_data(ean):
    """Obtiene datos del producto usando Open Food Facts API v2"""
    try:
        # Validar formato del EAN
        if not ean or not ean.isdigit() or len(ean) < 8 or len(ean) > 14:
            return {
                'success': False, 
                'error': 'El código EAN debe ser numérico y tener entre 8 y 14 dígitos'
            }
        
        # Usar API v2 con headers obligatorios
        url = f"https://world.openfoodfacts.org/api/v2/product/{ean}.json"
        headers = {
            "User-Agent": "MiApp/1.0 (miemail@example.com)"
        }
        
        print(f"Consultando API para EAN: {ean}")  # Debug
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status Code: {response.status_code}")  # Debug
        
        if response.status_code == 200:
            data = response.json()
            print(f"JSON Status: {data.get('status')}")  # Debug
            
            if data.get('status') == 1:
                product = data.get('product', {})
                print(f"Producto encontrado: {product.get('product_name', 'N/A')}")  # Debug
                
                return {
                    'success': True,
                    'data': {
                        'ean': ean,
                        'name': product.get('product_name', 'No disponible'),
                        'brand': product.get('brands', 'No disponible'),
                        'description': product.get('generic_name', 'No disponible'),
                        'category': product.get('categories', 'No disponible'),
                        'image_url': product.get('image_url', None),
                        'nutrition_grade': product.get('nutrition_grade_fr', 'No disponible'),
                        'ingredients': product.get('ingredients_text', 'No disponible'),
                        'allergens': product.get('allergens_tags', []),
                        'additives': product.get('additives_tags', []),
                        'nutriments': product.get('nutriments', {}),
                        'created_t': product.get('created_t', None),
                        'last_modified_t': product.get('last_modified_t', None)
                    }
                }
            else:
                # Producto no encontrado en la base de datos
                status_verbose = data.get('status_verbose', 'Producto no encontrado')
                return {
                    'success': False, 
                    'error': f'El producto con código EAN {ean} no se encuentra en nuestra base de datos. Verifica que el código sea correcto o intenta con otro producto.'
                }
        elif response.status_code == 404:
            return {
                'success': False, 
                'error': f'El producto con código EAN {ean} no existe en nuestra base de datos. Verifica que el código sea correcto.'
            }
        elif response.status_code == 429:
            return {
                'success': False, 
                'error': 'Demasiadas consultas. Por favor, espera un momento e intenta nuevamente.'
            }
        elif response.status_code >= 500:
            return {
                'success': False, 
                'error': 'Error del servidor. Por favor, intenta nuevamente en unos minutos.'
            }
        else:
            return {
                'success': False, 
                'error': f'Error de conexión (código {response.status_code}). Por favor, verifica tu conexión a internet e intenta nuevamente.'
            }
    except requests.exceptions.Timeout:
        return {
            'success': False, 
            'error': 'La consulta tardó demasiado tiempo. Por favor, verifica tu conexión a internet e intenta nuevamente.'
        }
    except requests.exceptions.ConnectionError:
        return {
            'success': False, 
            'error': 'No se pudo conectar al servidor. Por favor, verifica tu conexión a internet e intenta nuevamente.'
        }
    except Exception as e:
        return {
            'success': False, 
            'error': f'Error inesperado: {str(e)}. Por favor, intenta nuevamente.'
        }

def download_image(image_url, ean):
    """Descarga la imagen del producto"""
    try:
        response = requests.get(image_url, timeout=15)
        if response.status_code == 200:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{ean}_{timestamp}_original.jpg"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            return {'success': True, 'filepath': filepath, 'filename': filename}
        else:
            return {'success': False, 'error': f'Error descargando imagen: {response.status_code}'}
    except Exception as e:
        return {'success': False, 'error': f'Error descargando imagen: {str(e)}'}

def enhance_image_with_gemini(image_path, prompt, api_key):
    """Mejora la imagen usando Google Gemini API"""
    try:
        # Leer y codificar la imagen
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Preparar payload para Gemini
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent"
        headers = {
            "x-goog-api-key": api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        },
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }
            ]
        }
        
        # Llamar a la API
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            
            if "candidates" in data and data["candidates"]:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    for part in candidate["content"]["parts"]:
                        if "inlineData" in part:
                            # Decodificar imagen mejorada
                            img_bytes = base64.b64decode(part['inlineData']['data'])
                            image = Image.open(BytesIO(img_bytes))
                            
                            # Guardar imagen mejorada
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            ean = os.path.basename(image_path).split('_')[0]
                            filename = f"{ean}_{timestamp}_enhanced.png"
                            filepath = os.path.join(PROCESSED_FOLDER, filename)
                            
                            image.save(filepath)
                            return {'success': True, 'filepath': filepath, 'filename': filename}
            
            return {'success': False, 'error': 'No se pudo procesar la imagen con IA'}
        else:
            return {'success': False, 'error': f'Error API Gemini: {response.status_code}'}
    
    except Exception as e:
        return {'success': False, 'error': f'Error procesando imagen: {str(e)}'}

def create_excel_file(product_data, ean):
    """Crea archivo Excel con los datos del producto"""
    try:
        wb = Workbook()
        ws = wb.active
        ws.title = "Datos del Producto"
        
        # Encabezados
        headers = [
            'Campo', 'Valor'
        ]
        
        for col, header in enumerate(headers, 1):
            ws.cell(row=1, column=col, value=header)
        
        # Datos del producto
        data_rows = [
            ('EAN', product_data['ean']),
            ('Nombre', product_data['name']),
            ('Marca', product_data['brand']),
            ('Descripción', product_data['description']),
            ('Categoría', product_data['category']),
            ('Grado Nutricional', product_data['nutrition_grade']),
            ('Ingredientes', product_data['ingredients']),
            ('Alérgenos', ', '.join(product_data['allergens']) if product_data['allergens'] else 'Ninguno'),
            ('Aditivos', ', '.join(product_data['additives']) if product_data['additives'] else 'Ninguno'),
            ('Fecha Creación', datetime.fromtimestamp(product_data['created_t']).strftime('%Y-%m-%d %H:%M:%S') if product_data['created_t'] else 'No disponible'),
            ('Última Modificación', datetime.fromtimestamp(product_data['last_modified_t']).strftime('%Y-%m-%d %H:%M:%S') if product_data['last_modified_t'] else 'No disponible')
        ]
        
        for row, (field, value) in enumerate(data_rows, 2):
            ws.cell(row=row, column=1, value=field)
            ws.cell(row=row, column=2, value=value)
        
        # Ajustar ancho de columnas
        ws.column_dimensions['A'].width = 20
        ws.column_dimensions['B'].width = 50
        
        # Guardar archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{ean}_{timestamp}_datos.xlsx"
        filepath = os.path.join(PROCESSED_FOLDER, filename)
        wb.save(filepath)
        
        return {'success': True, 'filepath': filepath, 'filename': filename}
    
    except Exception as e:
        return {'success': False, 'error': f'Error creando Excel: {str(e)}'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_ean', methods=['POST'])
def process_ean():
    try:
        ean = request.form.get('ean', '').strip()
        
        if not ean:
            return jsonify({'success': False, 'error': 'EAN requerido'})
        
        # Obtener datos del producto
        product_result = get_product_data(ean)
        
        if not product_result['success']:
            return jsonify(product_result)
        
        product_data = product_result['data']
        result = {
            'success': True,
            'product_data': product_data,
            'images': {},
            'files': {}
        }
        
        # Descargar imagen original si existe
        if product_data['image_url']:
            image_result = download_image(product_data['image_url'], ean)
            if image_result['success']:
                result['images']['original'] = {
                    'filename': image_result['filename'],
                    'url': f"/static/uploads/{image_result['filename']}"
                }
                
                # Mejorar imagen con IA
                api_key = os.getenv("GEMINI_API_KEY")
                if api_key:
                    prompt = ("Take the provided product image as reference and enhance it for e-commerce. "
                            "Remove the background completely (make it transparent), center the product, "
                            "and show it from the front in a clean, clear, and attractive way. "
                            "Improve lighting, sharpness, and colors so the product looks professional "
                            "and appealing for online sales. Ensure the product remains realistic and "
                            "true to its original appearance.")
                    
                    enhance_result = enhance_image_with_gemini(image_result['filepath'], prompt, api_key)
                    if enhance_result['success']:
                        result['images']['enhanced'] = {
                            'filename': enhance_result['filename'],
                            'url': f"/static/processed/{enhance_result['filename']}"
                        }
                    else:
                        result['ai_error'] = enhance_result['error']
        
        # Crear archivo Excel
        excel_result = create_excel_file(product_data, ean)
        if excel_result['success']:
            result['files']['excel'] = {
                'filename': excel_result['filename'],
                'url': f"/download/{excel_result['filename']}"
            }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error procesando EAN: {str(e)}'})

@app.route('/download/<filename>')
def download_file(filename):
    try:
        filepath = os.path.join(PROCESSED_FOLDER, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return "Archivo no encontrado", 404
    except Exception as e:
        return f"Error descargando archivo: {str(e)}", 500

@app.route('/download_image/<path:filename>')
def download_image_file(filename):
    try:
        if filename.startswith('original'):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
        else:
            filepath = os.path.join(PROCESSED_FOLDER, filename)
        
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return "Archivo no encontrado", 404
    except Exception as e:
        return f"Error descargando imagen: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

