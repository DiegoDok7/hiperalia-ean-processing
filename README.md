# EAN Automation - Procesador de Productos con IA

## 🚀 Descripción

Aplicación web Flask para procesar códigos EAN de productos, obtener información detallada y mejorar imágenes con inteligencia artificial usando Google Gemini.

## ✨ Funcionalidades

### 📦 Procesamiento de Productos
- **Consulta EAN**: Obtiene información completa de productos usando Open Food Facts API v2
- **Datos nutricionales**: Información nutricional detallada (nutriments)
- **Validación robusta**: Validación de formato EAN (8-14 dígitos numéricos)
- **Manejo de errores**: Mensajes de error amigables y descriptivos

### 🖼️ Procesamiento de Imágenes
- **Descarga automática**: Descarga imagen original del producto si está disponible
- **Mejora con IA**: Mejora imágenes usando Google Gemini API
- **Fondo transparente**: Elimina fondo y centra el producto
- **Calidad e-commerce**: Optimización para ventas online

### 📊 Generación de Archivos
- **Excel con datos**: Archivo Excel con toda la información del producto
- **Imágenes mejoradas**: PNG con transparencia
- **Nombres únicos**: Timestamps para evitar conflictos
- **Descarga directa**: Descarga individual de cada archivo

## 🛠️ Instalación

### Requisitos
- Python 3.8+
- Cuenta de Google con API Key de Gemini

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd ean-automation
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**
Crear archivo `.env` en la raíz del proyecto:
```env
GEMINI_API_KEY=tu_api_key_aqui
```

4. **Ejecutar la aplicación**
```bash
cd scripts/web_app
python app.py
```

5. **Acceder a la aplicación**
Abrir navegador en: `http://127.0.0.1:5000`

## 📁 Estructura del Proyecto

```
ean-automation/
├── README.md                    # Documentación
├── requirements.txt             # Dependencias Python
├── .env                        # Variables de entorno (crear)
└── scripts/
    └── web_app/                # Aplicación Flask principal
        ├── app.py              # Aplicación Flask
        ├── templates/
        │   └── index.html      # Interfaz web
        └── static/
            ├── uploads/        # Imágenes originales
            └── processed/      # Imágenes mejoradas y Excel
```

## 🎯 Uso

### Interfaz Web
1. **Acceder**: `http://127.0.0.1:5000`
2. **Ingresar EAN**: Código de producto (ej: `8020458000348`)
3. **Procesar**: Hacer clic en "Procesar EAN"
4. **Ver resultados**: Información del producto, imágenes y archivos
5. **Descargar**: Botones de descarga para cada archivo

### EANs de Ejemplo
- `8020458000348` - Acqua Leggermente Frizzante
- `8017759011104` - Arborio Rice
- `8000270019599` - Granfetta integrale
- `8076809584531` - Sauce tomate à la pancetta Barilla

## 🔧 Configuración

### Variables de Entorno
```env
GEMINI_API_KEY=tu_api_key_de_google_gemini
```

### API Keys Requeridas
- **Google Gemini API**: Para mejora de imágenes
- **Open Food Facts**: Público, no requiere API key

## 📋 Dependencias

```
flask==2.3.3
werkzeug==2.3.7
requests==2.31.0
openpyxl==3.1.2
python-dotenv==1.0.0
gunicorn==21.2.0
pillow==10.0.1
```

## 🚨 Manejo de Errores

### Mensajes Amigables
- **EAN inválido**: "El código EAN debe ser numérico y tener entre 8 y 14 dígitos"
- **Producto no encontrado**: "El producto con código EAN {ean} no se encuentra en nuestra base de datos"
- **Error de conexión**: "No se pudo conectar al servidor. Verifica tu conexión a internet"
- **Timeout**: "La consulta tardó demasiado tiempo. Verifica tu conexión a internet"

### Códigos de Error HTTP
- **200**: Éxito
- **404**: Producto no encontrado
- **429**: Demasiadas consultas
- **500+**: Error del servidor

## 🎨 Características de la Interfaz

### Diseño Moderno
- **Responsive**: Adaptable a diferentes pantallas
- **Gradientes**: Diseño visual atractivo
- **Iconos**: FontAwesome para mejor UX
- **Animaciones**: Transiciones suaves

### Funcionalidades UX
- **Loading**: Indicador de progreso
- **Validación**: En tiempo real
- **Descarga**: Botones individuales
- **Errores**: Mensajes claros y útiles

## 🔍 Debugging

### Logs de Debug
La aplicación incluye logs detallados:
```
Consultando API para EAN: 8020458000348
Status Code: 200
JSON Status: 1
Producto encontrado: Acqua Leggermente Frizzante
```

### Archivos de Log
- **Consola**: Logs en tiempo real
- **Debug mode**: Activado por defecto

## 📈 Rendimiento

### Optimizaciones
- **Timeout**: 15 segundos para consultas
- **Headers**: User-Agent correcto para API
- **Caché**: Archivos estáticos optimizados
- **Compresión**: Imágenes optimizadas

### Límites
- **Rate limiting**: Respetado automáticamente
- **Tamaño de imagen**: Optimizado para web
- **Archivos**: Nombres únicos con timestamps

## 🤝 Contribución

### Desarrollo
1. Fork del repositorio
2. Crear rama feature
3. Commit cambios
4. Push a la rama
5. Crear Pull Request

### Reportar Issues
- Describir el problema
- Incluir pasos para reproducir
- Adjuntar logs si es necesario

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver archivo LICENSE para más detalles.

## 🆘 Soporte

### Problemas Comunes
1. **Error de API Key**: Verificar `.env` con `GEMINI_API_KEY`
2. **Puerto ocupado**: Cambiar puerto en `app.py`
3. **Dependencias**: Ejecutar `pip install -r requirements.txt`

### Contacto
- **Issues**: GitHub Issues
- **Documentación**: README.md
- **Logs**: Consola de la aplicación

---

**¡Disfruta procesando productos con IA!** 🚀