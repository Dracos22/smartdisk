from flask import Flask, render_template, jsonify, request
import subprocess
import psutil
import re

app = Flask(__name__, static_url_path='/static', static_folder='static')


def list_disks():
    try:
        result = subprocess.check_output(["lsblk", "-o", "NAME,TYPE", "-dn"]).decode()
        lines = result.strip().splitlines()
        disks = [f"/dev/{line.split()[0]}" for line in lines if "disk" in line]
        return disks
    except Exception as e:
        return [f"Error al escanear discos: {str(e)}"]


def get_disk_info(device):
    try:
        smartctl_cmd = ["sudo", "/usr/sbin/smartctl", "-a"]
        if "nvme" in device:
            smartctl_cmd += ["-d", "nvme"]
        smartctl_cmd.append(device)

        print("Ejecutando:", " ".join(smartctl_cmd))  # Debug

        proc = subprocess.run(smartctl_cmd, capture_output=True, text=True)
        output = proc.stdout
        error_output = proc.stderr

        print("STDOUT:\n", output)
        print("STDERR:\n", error_output)
        print("Return code:", proc.returncode)

        if not output.strip():
            raise Exception(error_output.strip() or "smartctl no devolvió salida.")

        if "PASSED" in output:
            health = ("verde", "Disco en buen estado.")
        elif "Warning" in output or "Pre-fail" in output:
            health = ("amarillo", "Advertencia: problemas detectados.")
        else:
            health = ("rojo", "Errores críticos detectados o sin verificación SMART.")

        model = re.search(r"Device Model:\s+(.*)", output) or re.search(r"Model Number:\s+(.*)", output)
        model = model.group(1).strip() if model else "Desconocido"

        capacity = re.search(r"User Capacity:\s+(.*)", output) or re.search(r"Total NVM Capacity:\s+(.*)", output)
        capacity = capacity.group(1).strip() if capacity else "Desconocida"

        usage = psutil.disk_usage('/')
        used_gb = round(usage.used / (1024 ** 3), 2)
        free_gb = round(usage.free / (1024 ** 3), 2)
        total_gb = round(usage.total / (1024 ** 3), 2)

        return {
            "status": health[0],
            "message": health[1],
            "model": model,
            "capacity": capacity,
            "used": f"{used_gb} GB",
            "free": f"{free_gb} GB",
            "total": f"{total_gb} GB",
            "device": device
        }

    except Exception as e:
        return {
            "status": "rojo",
            "message": f"Error inesperado: {str(e)}",
            "model": "N/A",
            "capacity": "N/A",
            "used": "N/A",
            "free": "N/A",
            "total": "N/A",
            "device": device
        }


@app.route("/")
def index():
    disks = list_disks()
    return render_template("index.html", disks=disks)


@app.route("/api/scan")
def scan():
    device = request.args.get("device", "/dev/sda")
    return jsonify(get_disk_info(device))


@app.route("/api/disks")
def api_disks():
    return jsonify(list_disks())


if __name__ == "__main__":
    app.run(debug=True)
