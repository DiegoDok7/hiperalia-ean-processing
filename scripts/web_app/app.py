from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for, Response, stream_with_context
import os
import json
import requests
from datetime import datetime
from PIL import Image
from io import BytesIO
import base64
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from dotenv import load_dotenv
import tempfile
import shutil
import zipfile
import time
import re
from rembg import remove

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
        print(f"🔍 get_product_data recibió EAN: '{ean}' (tipo: {type(ean)})")  # Debug
        
        # Validar formato del EAN
        if not ean or not ean.isdigit() or len(ean) < 8 or len(ean) > 14:
            print(f"❌ EAN inválido: '{ean}' (longitud: {len(ean) if ean else 0})")  # Debug
            return {
                'success': False, 
                'error': 'El código EAN debe ser numérico y tener entre 8 y 14 dígitos'
            }
        
        # Usar API v2 con headers obligatorios
        url = f"https://world.openfoodfacts.org/api/v2/product/{ean}.json"
        headers = {
            "User-Agent": "MiApp/1.0 (miemail@example.com)"
        }
        
        print(f"🔍 Consultando API para EAN: {ean}")  # Debug
        print(f"🔍 URL: {url}")  # Debug
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
    """Descarga la imagen del producto en memoria (no guarda archivos)"""
    try:
        response = requests.get(image_url, timeout=15)
        if response.status_code == 200:
            # Convertir a base64 para mostrar en la web sin guardar archivo
            image_base64 = base64.b64encode(response.content).decode('utf-8')
            return {
                'success': True, 
                'image_data': image_base64,
                'content_type': 'image/jpeg',
                'size': len(response.content)
            }
        else:
            return {'success': False, 'error': f'Error descargando imagen: {response.status_code}'}
    except Exception as e:
        return {'success': False, 'error': f'Error descargando imagen: {str(e)}'}

def enhance_image_with_gemini(image_data_base64, prompt, api_key):
    """Mejora la imagen usando Google Gemini API (trabaja en memoria)"""
    try:
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
                                "data": image_data_base64
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
                            # Devolver imagen mejorada como base64
                            enhanced_image_base64 = part['inlineData']['data']
                            return {
                                'success': True, 
                                'image_data': enhanced_image_base64,
                                'content_type': 'image/png'
                            }
            
            return {'success': False, 'error': 'No se pudo procesar la imagen con IA'}
        else:
            return {'success': False, 'error': f'Error API Gemini: {response.status_code}'}
    
    except Exception as e:
        return {'success': False, 'error': f'Error procesando imagen: {str(e)}'}

def remove_white_background(image_data_base64):
    """Remueve el fondo blanco de una imagen usando rembg"""
    try:
        # Decodificar la imagen base64
        image_bytes = base64.b64decode(image_data_base64)
        
        # Abrir imagen con PIL
        input_image = Image.open(BytesIO(image_bytes))
        
        # Remover fondo usando rembg
        output_image = remove(input_image)
        
        # Convertir a base64
        output_buffer = BytesIO()
        output_image.save(output_buffer, format='PNG')
        output_bytes = output_buffer.getvalue()
        output_base64 = base64.b64encode(output_bytes).decode('utf-8')
        
        return {
            'success': True,
            'image_data': output_base64,
            'content_type': 'image/png'
        }
    
    except Exception as e:
        return {'success': False, 'error': f'Error removiendo fondo: {str(e)}'}

def create_excel_data(product_data, ean):
    """Crea datos Excel en memoria (no guarda archivos)"""
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
        
        # Guardar en memoria como bytes
        from io import BytesIO
        excel_buffer = BytesIO()
        wb.save(excel_buffer)
        excel_data = excel_buffer.getvalue()
        excel_base64 = base64.b64encode(excel_data).decode('utf-8')
        
        return {
            'success': True, 
            'excel_data': excel_base64,
            'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'size': len(excel_data)
        }
    
    except Exception as e:
        return {'success': False, 'error': f'Error creando Excel: {str(e)}'}

@app.route('/')
def index():
    """Pantalla de inicio con opciones de búsqueda"""
    return render_template('index.html')

@app.route('/search_individual')
def search_individual():
    """Pantalla de búsqueda individual"""
    return render_template('search_individual.html')

@app.route('/search_bulk')
def search_bulk():
    """Pantalla de búsqueda por grupos"""
    return render_template('search_bulk.html')

@app.route('/process_ean', methods=['POST'])
def process_ean():
    try:
        ean = request.form.get('ean', '').strip()
        print(f"🔍 EAN recibido en process_ean: '{ean}'")  # Debug
        
        if not ean:
            return jsonify({'success': False, 'error': 'EAN requerido'})
        
        # Obtener datos del producto
        print(f"🔍 Llamando get_product_data con EAN: '{ean}'")  # Debug
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
                    'data': image_result['image_data'],
                    'content_type': image_result['content_type'],
                    'size': image_result['size']
                }
                
                # Mejorar imagen con IA
                api_key = os.getenv("GEMINI_API_KEY")
                if api_key:
                    prompt = ("Take the provided product image as reference and enhance it for e-commerce. "
                            "Remove the background completely (make it white), center the product, "
                            "and show it from the front in a clean, clear, and attractive way. "
                            "Improve lighting, sharpness, and colors so the product looks professional "
                            "and appealing for online sales. Ensure the product remains realistic and "
                            "true to its original appearance.")
                    
                    enhance_result = enhance_image_with_gemini(image_result['image_data'], prompt, api_key)
                    if enhance_result['success']:
                        # Remover fondo blanco usando rembg
                        remove_bg_result = remove_white_background(enhance_result['image_data'])
                        if remove_bg_result['success']:
                            result['images']['enhanced'] = {
                                'data': remove_bg_result['image_data'],
                                'content_type': remove_bg_result['content_type']
                            }
                        else:
                            # Si falla la remoción de fondo, usar la imagen mejorada con IA
                            result['images']['enhanced'] = {
                                'data': enhance_result['image_data'],
                                'content_type': enhance_result['content_type']
                            }
                            result['bg_removal_warning'] = remove_bg_result['error']
                    else:
                        result['ai_error'] = enhance_result['error']
        
        # Crear datos Excel
        excel_result = create_excel_data(product_data, ean)
        if excel_result['success']:
            result['files']['excel'] = {
                'data': excel_result['excel_data'],
                'content_type': excel_result['content_type'],
                'size': excel_result['size']
            }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error procesando EAN: {str(e)}'})

def sanitize_filename(name):
    """Sanitiza un nombre para usarlo como nombre de archivo"""
    if not name or name == 'No disponible':
        return 'sin_nombre'
    # Remover caracteres no válidos
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Limitar longitud
    name = name[:50]
    # Remover espacios al inicio y final
    name = name.strip()
    # Reemplazar espacios con guiones bajos
    name = name.replace(' ', '_')
    return name if name else 'sin_nombre'

def create_bulk_excel(products_data):
    """Crea un Excel con múltiples productos organizados por columnas"""
    try:
        wb = Workbook()
        ws = wb.active
        ws.title = "Productos"
        
        # Encabezados
        headers = [
            'EAN', 'Nombre', 'Marca', 'Descripción', 'Categoría',
            'Grado Nutricional', 'Ingredientes', 'Alérgenos', 'Aditivos',
            'Fecha Creación', 'Última Modificación'
        ]
        
        # Estilo para encabezados
        header_fill = PatternFill(start_color="333333", end_color="333333", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # Datos de productos
        for row_idx, product in enumerate(products_data, 2):
            ws.cell(row=row_idx, column=1, value=product.get('ean', 'N/A'))
            ws.cell(row=row_idx, column=2, value=product.get('name', 'No disponible'))
            ws.cell(row=row_idx, column=3, value=product.get('brand', 'No disponible'))
            ws.cell(row=row_idx, column=4, value=product.get('description', 'No disponible'))
            ws.cell(row=row_idx, column=5, value=product.get('category', 'No disponible'))
            ws.cell(row=row_idx, column=6, value=product.get('nutrition_grade', 'No disponible'))
            ws.cell(row=row_idx, column=7, value=product.get('ingredients', 'No disponible'))
            ws.cell(row=row_idx, column=8, value=', '.join(product.get('allergens', [])) if product.get('allergens') else 'Ninguno')
            ws.cell(row=row_idx, column=9, value=', '.join(product.get('additives', [])) if product.get('additives') else 'Ninguno')
            
            created_t = product.get('created_t')
            ws.cell(row=row_idx, column=10, value=datetime.fromtimestamp(created_t).strftime('%Y-%m-%d %H:%M:%S') if created_t else 'No disponible')
            
            last_modified_t = product.get('last_modified_t')
            ws.cell(row=row_idx, column=11, value=datetime.fromtimestamp(last_modified_t).strftime('%Y-%m-%d %H:%M:%S') if last_modified_t else 'No disponible')
        
        # Ajustar ancho de columnas
        for col in range(1, len(headers) + 1):
            ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 20
        
        # Guardar en memoria
        excel_buffer = BytesIO()
        wb.save(excel_buffer)
        excel_data = excel_buffer.getvalue()
        
        return excel_data
    
    except Exception as e:
        print(f"Error creando Excel bulk: {str(e)}")
        return None

@app.route('/process_bulk', methods=['POST'])
def process_bulk():
    """Procesa múltiples EANs y genera un ZIP con Excel e imágenes"""
    def generate():
        try:
            eans_json = request.form.get('eans', '[]')
            eans = json.loads(eans_json)
            
            if not eans:
                yield f"data: {json.dumps({'type': 'error', 'message': 'No se recibieron códigos EAN'})}\n\n"
                return
            
            products_data = []
            images_data = []
            
            # Procesar cada EAN
            for idx, ean in enumerate(eans):
                ean = ean.strip()
                
                # Obtener datos del producto
                product_result = get_product_data(ean)
                
                if product_result['success']:
                    product = product_result['data']
                    products_data.append(product)
                    
                    # Descargar y mejorar imagen si existe
                    if product['image_url']:
                        image_result = download_image(product['image_url'], ean)
                        if image_result['success']:
                             # Mejorar imagen con IA
                             api_key = os.getenv("GEMINI_API_KEY")
                             if api_key:
                                 prompt = ("Take the provided product image as reference and enhance it for e-commerce. "
                                         "Remove the background completely (make it white), center the product, "
                                         "and show it from the front in a clean, clear, and attractive way. "
                                         "Improve lighting, sharpness, and colors so the product looks professional "
                                         "and appealing for online sales. Ensure the product remains realistic and "
                                         "true to its original appearance.")
                                 
                                 enhance_result = enhance_image_with_gemini(image_result['image_data'], prompt, api_key)
                                 if enhance_result['success']:
                                     # Remover fondo blanco usando rembg
                                     remove_bg_result = remove_white_background(enhance_result['image_data'])
                                     if remove_bg_result['success']:
                                         # Sanitizar nombres para archivo
                                         name = sanitize_filename(product['name'])
                                         brand = sanitize_filename(product['brand'])
                                         filename = f"{name}-{brand}-{ean}.png"
                                         
                                         images_data.append({
                                             'filename': filename,
                                             'data': remove_bg_result['image_data']
                                         })
                                         
                                         yield f"data: {json.dumps({'type': 'progress', 'ean': ean, 'success': True, 'message': 'Procesado correctamente'})}\n\n"
                                     else:
                                         # Si falla la remoción de fondo, usar la imagen mejorada con IA
                                         name = sanitize_filename(product['name'])
                                         brand = sanitize_filename(product['brand'])
                                         filename = f"{name}-{brand}-{ean}.png"
                                         
                                         images_data.append({
                                             'filename': filename,
                                             'data': enhance_result['image_data']
                                         })
                                         
                                         yield f"data: {json.dumps({'type': 'progress', 'ean': ean, 'success': True, 'message': 'Procesado (sin remoción de fondo)'})}\n\n"
                                 else:
                                     yield f"data: {json.dumps({'type': 'progress', 'ean': ean, 'success': True, 'message': 'Procesado (sin mejora de imagen)'})}\n\n"
                             else:
                                 yield f"data: {json.dumps({'type': 'progress', 'ean': ean, 'success': True, 'message': 'Procesado (sin API key para IA)'})}\n\n"
                        else:
                            yield f"data: {json.dumps({'type': 'progress', 'ean': ean, 'success': True, 'message': 'Procesado (sin imagen)'})}\n\n"
                    else:
                        yield f"data: {json.dumps({'type': 'progress', 'ean': ean, 'success': True, 'message': 'Procesado (sin imagen disponible)'})}\n\n"
                else:
                    error_msg = product_result.get('error', 'Error desconocido')
                    yield f"data: {json.dumps({'type': 'progress', 'ean': ean, 'success': False, 'message': error_msg})}\n\n"
            
            # Crear archivo ZIP con Excel e imágenes
            if products_data:
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    # Agregar Excel
                    excel_data = create_bulk_excel(products_data)
                    if excel_data:
                        zip_file.writestr('productos.xlsx', excel_data)
                    
                    # Agregar imágenes en una carpeta
                    for img in images_data:
                        zip_file.writestr(f"imagenes/{img['filename']}", base64.b64decode(img['data']))
                
                zip_data = zip_buffer.getvalue()
                zip_base64 = base64.b64encode(zip_data).decode('utf-8')
                
                yield f"data: {json.dumps({'type': 'complete', 'zip_data': zip_base64})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'error', 'message': 'No se pudieron procesar productos'})}\n\n"
        
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': f'Error: {str(e)}'})}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

