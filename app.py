"""
Punto de entrada para Render.com
Importa la aplicación Flask desde scripts/web_app/app.py
"""

import sys
import os

# Agregar el directorio scripts/web_app al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts', 'web_app'))

# Importar la aplicación Flask
from app import app

# La variable app debe estar disponible para Gunicorn
if __name__ == '__main__':
    app.run(debug=True)
