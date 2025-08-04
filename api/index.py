#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API endpoint para Vercel
"""

import sys
import os

# Agregar el directorio padre al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar la aplicación Flask
from app import app

# Exportar la aplicación para Vercel
handler = app 