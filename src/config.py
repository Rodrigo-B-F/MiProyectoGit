# src/config.py
"""
Configuración centralizada de la aplicación.
Contiene constantes y rutas utilizadas en todo el proyecto.
"""

import os

# Ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ruta de la base de datos
DB_PATH = os.path.join(BASE_DIR, 'data', 'tienda.db')

# Configuraciones de la aplicación
APP_NAME = "Sistema de Gestión de Inventario"
APP_VERSION = "1.0.0"

# Configuraciones de productos
DEFAULT_DAYS_TO_EXPIRE_WARNING = 10  # Días antes de vencimiento para mostrar advertencia
