document.addEventListener("DOMContentLoaded", () => {
    const interfaceSelect = document.getElementById("interface");
    const resultDiv = document.getElementById("result");

    // Función para manejar errores
    function handleError(message) {
        console.error(message);
        resultDiv.innerHTML = `<pre class="error">Error: ${message}</pre>`;
    }

    // Cargar las interfaces WiFi
    fetch("/list_interfaces")
        .then(response => response.json())
        .then(data => {
            interfaceSelect.innerHTML = "";
            const wirelessInterfaces = data.interfaces.filter(iface => iface.startsWith("wl"));
            if (wirelessInterfaces.length === 0) {
                handleError("No se encontraron interfaces inalámbricas.");
                return;
            }
            wirelessInterfaces.forEach(iface => {
                const option = document.createElement("option");
                option.value = iface;
                option.textContent = iface;
                interfaceSelect.appendChild(option);
            });
        })
        .catch(err => handleError(`Error al cargar interfaces: ${err.message}`));

    // Escanear redes WiFi
    document.getElementById("scanWifiButton").addEventListener("click", async () => {
        const interface = interfaceSelect.value;
        if (!interface) {
            handleError("Selecciona una interfaz.");
            return;
        }
        try {
            const response = await fetch(`/scan_wifi?interface=${encodeURIComponent(interface)}`);
            const data = await response.json();
            if (data.networks) {
                resultDiv.innerHTML = `
                    <table>
                        <thead>
                            <tr>
                                <th>SSID</th>
                                <th>BSSID</th>
                                <th>Canal</th>
                                <th>Calidad</th>
                                <th>Encriptación</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.networks.map(network => `
                                <tr>
                                    <td>${network.SSID || "N/A"}</td>
                                    <td>${network.BSSID || "N/A"}</td>
                                    <td>${network.Channel || "N/A"}</td>
                                    <td>${network.Quality || "N/A"}</td>
                                    <td>${network.Encryption || "N/A"}</td>
                                </tr>
                            `).join("")}
                        </tbody>
                    </table>`;
            } else {
                handleError(data.error || "No se encontraron redes.");
            }
        } catch (error) {
            handleError(`Error al escanear redes: ${error.message}`);
        }
    });

    // Capturar handshake
    document.getElementById("captureHandshakeButton").addEventListener("click", async () => {
        const interface = interfaceSelect.value;
        const bssid = document.getElementById("bssid").value;
        const channel = document.getElementById("channel").value;

        if (!interface || !bssid || !channel) {
            handleError("Todos los campos son obligatorios.");
            return;
        }

        try {
            const response = await fetch("/capture_handshake", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    interface,
                    bssid,
                    channel
                }),
            });
            const data = await response.json();
            if (data.error) {
                handleError(data.error);
            } else {
                resultDiv.innerHTML = `<pre>Handshake capturado con éxito: ${JSON.stringify(data, null, 2)}</pre>`;
            }
        } catch (error) {
            handleError(`Error al capturar handshake: ${error.message}`);
        }
    });

    // Espacio para el cracking de contraseñas

    // Función para actualizar el nombre del archivo .cap seleccionado
    document.getElementById('selectCapFileButton').addEventListener('click', function() {
        document.getElementById('capFile').click();
    });

    document.getElementById('capFile').addEventListener('change', function(event) {
        if (event.target.files.length > 0) {
            document.getElementById('capFileName').textContent = event.target.files[0].name;
        } else {
            document.getElementById('capFileName').textContent = 'Ningún archivo seleccionado';
        }
    });

    // Función para actualizar el nombre del archivo de diccionario seleccionado
    document.getElementById('selectDictFileButton').addEventListener('click', function() {
        document.getElementById('dictFile').click();
    });

    document.getElementById('dictFile').addEventListener('change', function(event) {
        if (event.target.files.length > 0) {
            document.getElementById('dictFileName').textContent = event.target.files[0].name;
        } else {
            document.getElementById('dictFileName').textContent = 'Ningún archivo seleccionado';
        }
    });

    // Botón para iniciar el cracking (simulación de proceso)
    document.getElementById('crackPasswordButton').addEventListener('click', () => {
        const capFile = document.getElementById('capFile').files[0];
        const dictFile = document.getElementById('dictFile').files[0];

        if (!capFile || !dictFile) {
            handleError("Debes seleccionar un archivo .cap y un archivo de diccionario.");
            return;
        }

        // Aquí agregarías la lógica para enviar los archivos al backend para el cracking de contraseñas
        resultDiv.innerHTML = "<pre>Iniciando el proceso de cracking...</pre>";

        // Ejemplo de cómo enviar los archivos al backend (suponiendo que tienes una ruta en el servidor para eso)
        const formData = new FormData();
        formData.append("capFile", capFile);
        formData.append("dictFile", dictFile);

        fetch("/crack_password", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                handleError(data.error);
            } else {
                resultDiv.innerHTML = `<pre>Resultado del cracking: ${JSON.stringify(data, null, 2)}</pre>`;
            }
        })
        .catch(error => handleError(`Error al hacer cracking: ${error.message}`));
    });
});
