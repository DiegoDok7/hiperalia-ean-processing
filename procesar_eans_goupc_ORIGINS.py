#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para procesar códigos EAN desde archivo usando GO-UPC API
y generar Excel completo con toda la información
"""

import os
from datetime import datetime
from goupc_automation import (
    leer_codigos_desde_archivo,
    procesar_codigos_goupc,
    procesar_codigos_con_reintentos,
    guardar_excel_goupc,
    guardar_json
)

def main():
    """
    Función principal para procesar EANs y generar Excel
    """
    print("🚀 PROCESAMIENTO DE CÓDIGOS EAN CON GO-UPC + IA")
    print("=" * 60)
    
    # Configuración
    archivo_eans = input("📁 Ingresa la ruta del archivo .txt con códigos EAN: ").strip()
    if not archivo_eans:
        archivo_eans = "codigosean.txt"  # Archivo por defecto en el directorio actual
    
    downloads_path = os.path.expanduser("~/Downloads")
    
    # Generar nombres de archivos con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_filename = f"productos_goupc_{timestamp}.xlsx"
    json_filename = f"productos_goupc_{timestamp}.json"
    
    excel_path = os.path.join(downloads_path, excel_filename)
    json_path = os.path.join(downloads_path, json_filename)
    
    print(f"📁 Archivo de códigos: {archivo_eans}")
    print(f"💾 Excel de salida: {excel_path}")
    print(f"📄 JSON de salida: {json_path}")
    print()
    
    # Verificar que existe el archivo de códigos
    if not os.path.exists(archivo_eans):
        print(f"❌ Error: No se encontró el archivo {archivo_eans}")
        return False
    
    try:
        # 1. Leer códigos EAN desde archivo
        print("📖 PASO 1: Leyendo códigos EAN...")
        codigos = leer_codigos_desde_archivo(archivo_eans)
        
        if not codigos:
            print("❌ No se encontraron códigos válidos en el archivo")
            return False
        
        print(f"✅ {len(codigos)} códigos EAN leídos correctamente")
        print("Códigos encontrados:", codigos[:5], "..." if len(codigos) > 5 else "")
        print()
        
        # 2. Procesar códigos con GO-UPC API (con reintentos y IA)
        print("🔍 PASO 2: Consultando GO-UPC API con reintentos y completado con IA...")
        resultados = procesar_codigos_con_reintentos(codigos)
        
        if not resultados:
            print("❌ No se obtuvieron resultados")
            return False
        
        # 3. Mostrar estadísticas
        print("\n📊 ESTADÍSTICAS:")
        print("-" * 40)
        encontrados = len([r for r in resultados if r.get('producto_encontrado')])
        errores = len([r for r in resultados if r.get('error')])
        completados_ia = len([r for r in resultados if r.get('datos_completados_ia')])
        reintentos = len([r for r in resultados if r.get('intentos', 1) > 1])
        
        print(f"Total procesados: {len(resultados)}")
        print(f"Productos encontrados: {encontrados}")
        print(f"No encontrados: {len(resultados) - encontrados}")
        print(f"Errores: {errores}")
        print(f"Completados con IA: {completados_ia}")
        print(f"Reintentos realizados: {reintentos}")
        print(f"Tasa de éxito: {(encontrados/len(resultados)*100):.1f}%")
        
        # 4. Mostrar algunos productos encontrados
        productos_encontrados = [r for r in resultados if r.get('producto_encontrado')]
        if productos_encontrados:
            print(f"\n🎯 PRODUCTOS ENCONTRADOS (primeros {min(3, len(productos_encontrados))}):")
            print("-" * 50)
            for i, producto in enumerate(productos_encontrados[:3], 1):
                print(f"{i}. {producto.get('nombre_producto', 'N/A')}")
                print(f"   Marca: {producto.get('marca', 'N/A')}")
                print(f"   Categoría: {producto.get('categoria', 'N/A')}")
                print()
        
        # 5. Guardar resultados en Excel
        print("💾 PASO 3: Generando archivo Excel...")
        guardar_excel_goupc(resultados, excel_path)
        
        # 6. Guardar respaldo en JSON
        print("📄 PASO 4: Generando respaldo JSON...")
        guardar_json(resultados, json_path)
        
        # 7. Resumen final
        print("\n🎉 PROCESAMIENTO COMPLETADO")
        print("=" * 60)
        print(f"✅ Archivo Excel: {excel_path}")
        print(f"✅ Archivo JSON: {json_path}")
        print(f"📊 {encontrados}/{len(resultados)} productos con información completa")
        
        # Información sobre el Excel generado
        print(f"\n📋 El archivo Excel contiene:")
        print(f"   • Hoja 'Productos GO-UPC': Información principal con datos de IA")
        print(f"   • Hoja 'Especificaciones': Detalles técnicos")
        print(f"   • {len(resultados)} filas de datos")
        print(f"   • Información completa de GO-UPC API")
        print(f"   • Datos completados con IA: {completados_ia} productos")
        print(f"   • Información de reintentos y errores")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante el procesamiento: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n🚀 ¡Listo! Revisa tu carpeta de Descargas para ver los archivos generados.")
    else:
        print(f"\n⚠️ El procesamiento no se completó correctamente.")
    
    input("\nPresiona Enter para cerrar...") 