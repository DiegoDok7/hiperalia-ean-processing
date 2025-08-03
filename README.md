# EAN Automation - Procesador de Códigos EAN

Procesador de códigos EAN que utiliza la API de GO-UPC para obtener información de productos y genera archivos Excel con datos completos.

## 🚀 Características

- **API GO-UPC**: Consulta automática a la base de datos de productos
- **Inteligencia Artificial**: Completado inteligente de datos faltantes con OpenAI
- **Reintentos automáticos**: Manejo robusto de errores de API
- **Interfaz web**: Aplicación Flask con interfaz moderna
- **Exportación Excel**: Generación de archivos Excel completos con formato profesional

## 📋 Archivos Principales

- `procesar_eans_goupc_ORIGINS.py` - Script principal para procesar códigos EAN
- `goupc_automation.py` - Funciones core de procesamiento y API
- `app.py` - Aplicación web Flask
- `templates/index.html` - Interfaz de usuario

## ⚙️ Configuración

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar API keys:**
   - Copia `config.py.example` a `config.py`
   - O crea un archivo `.env` basado en `env_template.txt`
   - Configura tu `GO_UPC_API_KEY` (requerida)
   - Configura tu `OPENAI_API_KEY` (opcional, para IA)

## 🎯 Uso

### Opción 1: Script Directo
```bash
python procesar_eans_goupc_ORIGINS.py
```

### Opción 2: Interfaz Web
```bash
python app.py
```
Luego abre: http://localhost:5000

## 📁 Estructura del Proyecto

```
ean-automation/
├── procesar_eans_goupc_ORIGINS.py  # Script principal
├── goupc_automation.py             # Funciones core
├── app.py                          # Aplicación web
├── templates/
│   └── index.html                  # Interfaz de usuario
├── requirements.txt                # Dependencias
├── config.py.example              # Template de configuración
└── env_template.txt               # Template de variables de entorno
```

## 🔧 Dependencias

- `requests` - Consultas HTTP
- `openai` - API de OpenAI para IA
- `openpyxl` - Generación de Excel
- `python-dotenv` - Variables de entorno
- `flask` - Aplicación web
- `werkzeug` - Utilidades web

## 📊 Formato de Entrada

Archivo `.txt` con un código EAN por línea:
```
8001040016558
8009004600201
843248155091
```

## 📈 Formato de Salida

Archivo Excel con:
- **Hoja "Productos GO-UPC"**: Información principal
- **Hoja "Especificaciones"**: Detalles técnicos
- Datos completados con IA
- Estadísticas de procesamiento 