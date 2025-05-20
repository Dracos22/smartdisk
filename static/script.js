function fetchDisks() {
    fetch("/api/disks")
        .then(res => res.json())
        .then(disks => {
            const select = document.getElementById("diskSelect");
            select.innerHTML = "";
            disks.forEach(d => {
                const option = document.createElement("option");
                option.value = d;
                option.textContent = d;
                select.appendChild(option);
            });
        });
}

function startScan() {
    const device = document.getElementById("diskSelect").value;
    fetch(`/api/scan?device=${encodeURIComponent(device)}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById("result").innerHTML = `
                <div class="status ${data.status}"><strong>${data.message}</strong></div>
                <div class="info-box">
                    <p><strong>Dispositivo:</strong> ${data.device}</p>
                    <p><strong>Modelo:</strong> ${data.model}</p>
                    <p><strong>Capacidad declarada:</strong> ${data.capacity}</p>
                    <p><strong>Espacio total:</strong> ${data.total}</p>
                    <p><strong>Espacio usado:</strong> ${data.used}</p>
                    <p><strong>Espacio libre:</strong> ${data.free}</p>
                </div>
            `;
        }).catch(err => {
            document.getElementById("result").innerHTML = `<p>Error: ${err}</p>`;
        });
}

document.addEventListener("DOMContentLoaded", () => {
    fetchDisks();
});
