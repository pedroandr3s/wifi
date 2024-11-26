document.addEventListener("DOMContentLoaded", () => {
    const interfaceSelect = document.getElementById("monitorInterface");
    const resultDiv = document.getElementById("monitorResult");
    const messageDiv = document.getElementById("monitorMessages");

    // Función para mostrar mensajes
    function showMessage(message, type = "info") {
        messageDiv.innerHTML = `<p class="${type}">${message}</p>`;
    }

    // Fetch interfaces
    fetch("/list_interfaces")
        .then(response => response.json())
        .then(data => {
            interfaceSelect.innerHTML = "";
            const wirelessInterfaces = data.interfaces.filter(iface =>
                iface.startsWith("wl")
            );
            if (wirelessInterfaces.length === 0) {
                showMessage("No se encontraron interfaces inalámbricas.", "error");
                return;
            }
            wirelessInterfaces.forEach(iface => {
                const option = document.createElement("option");
                option.value = iface;
                option.textContent = iface;
                interfaceSelect.appendChild(option);
            });
        })
        .catch(err => showMessage(`Error al obtener las interfaces: ${err.message}`, "error"));

    // Start Monitor Mode
    document.getElementById("startMonitorButton").addEventListener("click", async () => {
        const iface = interfaceSelect.value;
        if (!iface) {
            showMessage("Selecciona una interfaz válida.", "error");
            return;
        }
        try {
            const response = await fetch("/start_monitor_mode", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: `interface=${encodeURIComponent(iface)}`,
            });
            const data = await response.json();
            showMessage(data.message || "Modo monitor activado correctamente.");
        } catch (error) {
            showMessage(`Error al activar modo monitor: ${error.message}`, "error");
        }
    });

    // Stop Monitor Mode
    document.getElementById("stopMonitorButton").addEventListener("click", async () => {
        const iface = interfaceSelect.value;
        if (!iface) {
            showMessage("Selecciona una interfaz válida.", "error");
            return;
        }
        try {
            const response = await fetch("/stop_monitor_mode", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: `interface=${encodeURIComponent(iface)}`,
            });
            const data = await response.json();
            showMessage(data.message || "Modo monitor desactivado correctamente.");
        } catch (error) {
            showMessage(`Error al desactivar modo monitor: ${error.message}`, "error");
        }
    });

    // Reset Interface
    document.getElementById("resetInterfaceButton").addEventListener("click", async () => {
        const iface = interfaceSelect.value;
        if (!iface) {
            showMessage("Selecciona una interfaz válida.", "error");
            return;
        }
        try {
            const response = await fetch("/reset_interface", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: `interface=${encodeURIComponent(iface)}`,
            });
            const data = await response.json();
            showMessage(data.message || "Interfaz reiniciada correctamente.");
        } catch (error) {
            showMessage(`Error al reiniciar la interfaz: ${error.message}`, "error");
        }
    });
});
