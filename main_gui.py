import sys
import os

# --- Configuración de ruta para importaciones ---
# Permite ejecutar este script desde la raíz del proyecto
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from models import init_db
from views.gui import run

def main():
    """Función principal del GUI"""
    
    # Inicialización de la Base de Datos
    print("Inicializando base de datos...")
    init_db()
    print("Base de datos lista.")
    
    # Ejecutar GUI
    run()

if __name__ == "__main__":
    main()
