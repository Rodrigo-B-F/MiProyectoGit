Project Structure

MiProyectoGit
├── docs
│   └── arquitectura.md      # Documentación.
├── mi_entorno               # Entorno virtual (debe ser ignorado por Git).
│   └── ...
├── src                      # Código Fuente Principal
│   ├── __pycache__
│   │   └── ... (.pyc files)
│   ├── backend              # Lógica de Negocio
│   │   ├── __pycache__
│   │   │   └── ... (.pyc files)
│   │   ├── models.py
│   │   └── services.py
│   ├── data                 # Archivos de datos estáticos y base de datos
│   │   └── tienda.db        # ¡Ubicación confirmada!
│   ├── utils                # Funciones de utilidad.
│   ├── cli.py               # Herramientas de línea de comandos.
│   ├── init_db.py           # Lógica de inicialización de la DB.
│   └── tui.py               # Interfaz en la terminal. 
├── tests                    # Carpeta para pruebas.
├── Github.txt
├── README.md
└── requirements.txt         # Dependencias.