from flask import jsonify, request, render_template
from services import (
    start_monitor_mode,
    stop_monitor_mode,
    scan_wifi,
    list_interfaces,
    reset_interface,
    deauth_attack,
    save_scan_results_to_csv,
    save_scan_results_to_json
)
import logging

def register_routes(app):
    @app.route("/", methods=["GET"])
    def index():
        """Ruta para cargar la página principal."""
        logging.info("Ruta raíz / llamada")
        return render_template("index.html")

    @app.route("/audit_panel", methods=["GET"])
    def audit_panel():
        """Ruta para cargar el panel de auditoría."""
        logging.info("Ruta /audit_panel llamada")
        return render_template("audit_panel.html")

    @app.route("/monitor_mode", methods=["GET"])
    def monitor_mode():
        """Ruta para cargar la página de modo monitor."""
        logging.info("Ruta /monitor_mode llamada")
        return render_template("monitor_mode.html")

    @app.route("/list_interfaces", methods=["GET"])
    def interfaces():
        """Ruta para listar las interfaces de red disponibles."""
        logging.info("Ruta /list_interfaces llamada")
        interfaces = list_interfaces()
        if not interfaces:
            return jsonify({"error": "No se encontraron interfaces de red"}), 404
        return jsonify({"interfaces": interfaces}), 200

    @app.route("/start_monitor_mode", methods=["POST"])
    def start_monitor():
        """Ruta para iniciar el modo monitor en una interfaz."""
        interface = request.form.get("interface")
        if not interface:
            logging.warning("Interfaz no proporcionada en /start_monitor_mode")
            return jsonify({"error": "Interfaz no proporcionada"}), 400
        logging.info(f"Iniciando modo monitor en la interfaz: {interface}")
        return start_monitor_mode(interface)

    @app.route("/stop_monitor_mode", methods=["POST"])
    def stop_monitor():
        """Ruta para detener el modo monitor en una interfaz."""
        interface = request.form.get("interface")
        if not interface:
            logging.warning("Interfaz no proporcionada en /stop_monitor_mode")
            return jsonify({"error": "Interfaz no proporcionada"}), 400
        logging.info(f"Deteniendo modo monitor en la interfaz: {interface}")
        return stop_monitor_mode(interface)

    @app.route("/scan_wifi", methods=["GET"])
    def scan():
        """Ruta para escanear redes Wi-Fi usando una interfaz."""
        interface = request.args.get("interface")
        if not interface:
            logging.warning("Interfaz no proporcionada en /scan_wifi")
            return jsonify({"error": "Interfaz no proporcionada"}), 400
        logging.info(f"Escaneando redes Wi-Fi con la interfaz: {interface}")
        networks, status_code = scan_wifi(interface)
        if status_code != 200:
            return jsonify(networks), status_code

        # Guardar los resultados en CSV y JSON
        save_scan_results_to_csv(networks)
        save_scan_results_to_json(networks)
        return jsonify({"networks": networks}), 200

    @app.route("/reset_interface", methods=["POST"])
    def reset():
        """Ruta para reiniciar una interfaz de red."""
        interface = request.form.get("interface")
        if not interface:
            logging.warning("Interfaz no proporcionada en /reset_interface")
            return jsonify({"error": "Interfaz no proporcionada"}), 400
        logging.info(f"Reiniciando la interfaz: {interface}")
        return reset_interface(interface)

    @app.route("/deauth_attack", methods=["POST"])
    def deauth():
        """Ruta para iniciar un ataque de desautenticación."""
        data = request.get_json()
        interface = data.get('interface')
        bssid = data.get('bssid')
        client_mac = data.get('client_mac')
        
        if not interface or not bssid:
            logging.warning("Interfaz o BSSID no proporcionados en /deauth_attack")
            return jsonify({"error": "Interfaz o BSSID no proporcionados"}), 400

        logging.info(f"Iniciando ataque de desautenticación en la interfaz: {interface}, BSSID: {bssid}, Cliente: {client_mac}")
        try:
            deauth_attack(interface, bssid, client_mac)
            return jsonify({"status": "success"}), 200
        except Exception as e:
            logging.error(f"Error en /deauth_attack: {e}")
            return jsonify({"error": str(e)}), 500
