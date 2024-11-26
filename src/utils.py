import subprocess
import logging

def execute_command(command):
    """Ejecuta un comando en la terminal y retorna su salida."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
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
        return interfaces
    except Exception as e:
        logging.error(f"Error al listar interfaces: {e}")
        return []
