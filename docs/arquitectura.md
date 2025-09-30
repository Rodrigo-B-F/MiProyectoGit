Project Structure

MiProyectoGit/
├── src/
│   ├── app.py                # Aplicación principal con Streamlit (interfaz gráfica)
|   ├── init_db.py
|   ├── cli.py                # Aplicación en la terminal
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── models.py         # Definición de tablas (Peewee ORM)
│   │   ├── data_loader.py    # Importar/exportar datos, inicialización de BD
│   │   └── services.py       # Lógica de negocio (ventas, movimientos de stock, etc.)
│   ├── data/
|   |   └── tienda.db         # Base de datos SQLite manejada por Peewee
|   └── utils/
│       └── helpers.py        # Funciones utilitarias (validaciones, formateo, etc.)
├── tests/
│   └── test_models.py        # Pruebas unitarias para validar los modelos
├── docs/
│   └── arquitectura.md       # Documentación de la estructura
├── requirements.txt          # Librerías necesarias
├── README.md                 # Instrucciones del proyecto
└── LICENSE