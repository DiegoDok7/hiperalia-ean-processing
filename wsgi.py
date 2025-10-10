"""
Punto de entrada WSGI para Render.com
Importa la aplicación Flask desde scripts/web_app/app.py
"""

import sys
import os
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("=" * 60)
logger.info("🚀 INICIANDO WSGI - EAN-AUTOMATION")
logger.info("=" * 60)

# Agregar el directorio scripts/web_app al path
logger.info(f"📂 Directorio actual: {os.getcwd()}")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts', 'web_app'))
logger.info(f"✓ Path actualizado")

# Importar la aplicación Flask
try:
    logger.info("📦 Importando aplicación Flask desde app...")
    from app import app
    logger.info("✅ Aplicación Flask importada exitosamente en WSGI!")
except Exception as e:
    logger.error(f"❌ ERROR FATAL en WSGI al importar app: {e}", exc_info=True)
    raise

logger.info("🎯 WSGI listo para servir aplicación")

if __name__ == '__main__':
    logger.info("🚀 Iniciando en modo desarrollo desde WSGI...")
    app.run(debug=True)
