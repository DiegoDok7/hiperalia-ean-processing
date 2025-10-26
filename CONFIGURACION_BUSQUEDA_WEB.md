# 🔍 Configuración de Búsqueda Web de Imágenes

## 📋 Resumen

He implementado una funcionalidad de búsqueda web de imágenes que puede encontrar imágenes de productos en internet usando **Serper API** (gratuita con límite).

## 🚀 Funcionalidades Implementadas

### 1. **Nueva Función: `search_web_images()`**
- Busca imágenes en Google usando Serper API
- Intenta descargar hasta 5 imágenes por producto
- Valida que las imágenes sean válidas y tengan buen tamaño
- Fallback automático a fuentes tradicionales si falla

### 2. **Página de Prueba: `/test_web_search`**
- Interfaz para probar los 9 EANs específicos que mencionaste
- Muestra resultados en tiempo real con imágenes
- Progreso visual del procesamiento
- Tarjetas de resultado con información detallada

### 3. **Integración Automática**
- La búsqueda web se ejecuta automáticamente en todos los modos
- Si encuentra imagen web, la usa; si no, usa fuentes tradicionales
- No requiere cambios en el flujo existente

## ⚙️ Configuración Requerida

### 1. **Obtener API Key de Serper**
1. Ve a [serper.dev](https://serper.dev)
2. Regístrate (gratis)
3. Obtén tu API key
4. Agrega a tu archivo `.env`:
   ```
   SERPER_API_KEY=tu_api_key_aqui
   ```

### 2. **Límites de Serper**
- **Gratis**: 2,500 búsquedas por mes
- **Pago**: Desde $5/mes para más búsquedas
- **Velocidad**: 10 búsquedas por segundo

## 🎯 EANs de Prueba Configurados

Los siguientes EANs están preconfigurados para prueba:

```
8001250120885
8001250121202
8005121002102
8005121040845
8005121000290
8005121000429
8005121002584
8005121002850
8005121052862
```

## 📱 Cómo Usar

### Opción 1: Página de Prueba
1. Ve a la página principal
2. Haz clic en "Prueba Búsqueda Web"
3. Haz clic en "Buscar Imágenes en la Web"
4. Ve los resultados en tiempo real

### Opción 2: Modo Normal
1. Usa cualquiera de los modos existentes (Individual, Grupos, Solo Imágenes)
2. La búsqueda web se ejecuta automáticamente
3. Si encuentra imagen web, la usa; si no, usa fuentes tradicionales

## 🔄 Flujo de Búsqueda

```
1. Recibe EAN + nombre del producto
2. Busca en Google usando Serper API
3. Obtiene hasta 5 resultados de imágenes
4. Intenta descargar cada imagen
5. Valida tamaño y formato
6. Retorna la primera imagen válida encontrada
7. Si falla, usa fuentes tradicionales (OpenFoodFacts, EAN-Search)
```

## 📊 Ventajas de la Búsqueda Web

### ✅ **Ventajas:**
- **Más fuentes**: Acceso a millones de imágenes en internet
- **Mejor calidad**: Imágenes de tiendas online, fabricantes, etc.
- **Más actualizadas**: Imágenes más recientes
- **Diversidad**: Diferentes ángulos y presentaciones

### ⚠️ **Consideraciones:**
- **Costo**: Requiere API key (gratis con límite)
- **Velocidad**: Más lento que fuentes tradicionales
- **Dependencia**: Requiere conexión a internet estable

## 🛠️ Archivos Modificados

1. **`app.py`**:
   - Nueva función `search_web_images()`
   - Modificada `search_and_download_product_image()`
   - Nueva ruta `/test_web_search`
   - Nueva ruta `/test_single_ean`

2. **`templates/test_web_search.html`**:
   - Página de prueba con interfaz moderna
   - Progreso en tiempo real
   - Tarjetas de resultados con imágenes

3. **`templates/index.html`**:
   - Nueva opción "Prueba Búsqueda Web"

## 🚀 Próximos Pasos

1. **Configura la API key** de Serper en tu `.env`
2. **Prueba la funcionalidad** con los EANs preconfigurados
3. **Ajusta los parámetros** si es necesario (número de resultados, filtros, etc.)
4. **Monitorea el uso** para no exceder los límites gratuitos

## 💡 Recomendaciones

- **Para pruebas**: Usa la página de prueba primero
- **Para producción**: La búsqueda web se ejecuta automáticamente
- **Monitoreo**: Revisa los logs para ver qué fuentes funcionan mejor
- **Fallback**: Siempre tiene respaldo con fuentes tradicionales

¡La funcionalidad está lista para usar! 🎉
