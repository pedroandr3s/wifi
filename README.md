# WiFi Audit Tool

Esta es una herramienta de auditoría WiFi basada en Flask que interactúa con herramientas como `aircrack-ng` para realizar auditorías de redes WiFi.

## Estructura del Proyecto
wifi_audit/
│
├── src/
│   ├── app.py
│   ├── routes.py
│   ├── services.py
│   ├── utils.py
│   ├── templates/
│   │   ├── index.html
│   │   ├── audit_panel.html
│   │   └── monitor_mode.html
│   ├── static/
│   │   ├── js/
│   │   │   └── scripts.js
│   │   ├── css/
│   │   │   └── styles.css
│   │   └── images/
│   │       └── logo.png
│   └── logs/
│       └── audit_logs.log
├── README.md
├── requirements.txt
├── .gitignore
└── venv/  # Entorno virtual (si necesario, fuera de src)


## Instalación

1. Clona el repositorio:
    ```bash
    git clone https://github.com/tu_usuario/wifi_audit.git
    cd wifi_audit
    ```

2. Crea y activa un entorno virtual:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
    ```

3. Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

## Uso

1. Ejecuta la aplicación:
    ```bash
    flask run
    ```

2. Abre tu navegador y ve a `http://127.0.0.1:5000`.

## Estructura del Código

- `app.py`: Archivo principal para inicializar Flask.
- `routes.py`: Registro y gestión de rutas Flask.
- `services.py`: Funciones y lógica del backend.
- `utils.py`: Funciones reutilizables y utilidades.
- `templates/`: Carpeta para las plantillas HTML.
- `static/`: Carpeta para archivos estáticos.
- `logs/`: Carpeta para los logs.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o un pull request para discutir cualquier cambio que te gustaría hacer.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT.


Actualizacion de Readme
// Activar la interfaz de red inalámbrica wlan0
ip link set wlan0 up

Para crackeo luego de handshake 
// Cambiar permisos del directorio para que el propietario pueda leer, escribir y ejecutar, mientras que otros solo puedan leer y ejecutar
sudo chmod 755 /home/kali/wifi_audit/src

// Cambiar permisos del archivo .cap para que el propietario pueda leer y escribir, mientras que otros solo puedan leer
sudo chmod 644 /home/kali/wifi_audit/src/handshake_24CF24285433-01.cap

// Cambiar la propiedad del archivo .cap al usuario y grupo 'kali' para asegurar el control total del archivo por dicho usuario
sudo chown kali:kali /home/kali/wifi_audit/src/handshake_24CF24285433-01.cap

