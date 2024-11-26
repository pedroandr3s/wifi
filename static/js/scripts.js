document.addEventListener("DOMContentLoaded", () => {
    const interfaceSelect = document.getElementById("interface");

    // Fetch available interfaces
    fetch("/list_interfaces")
        .then(response => response.json())
        .then(data => {
            interfaceSelect.innerHTML = "";
            data.forEach(iface => {
                const option = document.createElement("option");
                option.value = iface;
                option.textContent = iface;
                interfaceSelect.appendChild(option);
            });
        })
        .catch(err => console.error("Error fetching interfaces:", err));

    // Manejar el envío del formulario para iniciar modo monitor
    const startForm = document.getElementById("startMonitorModeForm");
    if (startForm) {
        startForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const interface = document.getElementById("interface").value;

            const response = await fetch("/start_monitor_mode", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: `interface=${encodeURIComponent(interface)}`
            });

            const result = await response.json();
            document.getElementById("result").innerHTML = `<pre>${result.message || result.error}</pre>`;
        });
    }

    // Manejar el envío del formulario para detener modo monitor
    const stopForm = document.getElementById("stopMonitorModeForm");
    if (stopForm) {
        stopForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const interface = document.getElementById("interface").value;

            const response = await fetch("/stop_monitor_mode", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: `interface=${encodeURIComponent(interface)}`
            });

            const result = await response.json();
            document.getElementById("result").innerHTML = `<pre>${result.message || result.error}</pre>`;
        });
    }

    // Manejar el envío del formulario para reiniciar la interfaz
    const resetForm = document.getElementById("resetInterfaceForm");
    if (resetForm) {
        resetForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const interface = document.getElementById("interface").value;

            const response = await fetch("/reset_interface", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: `interface=${encodeURIComponent(interface)}`
            });

            const result = await response.json();
            document.getElementById("result").innerHTML = `<pre>${result.message || result.error}</pre>`;
        });
    }
});
