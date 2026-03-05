import os
import shutil
import subprocess
import time
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, url_for

app = Flask(__name__)
PROCESS_START_TS = time.time()


def _running_in_docker():
    if os.path.exists("/.dockerenv"):
        return True

    cgroup_path = "/proc/1/cgroup"
    if os.path.exists(cgroup_path):
        try:
            with open(cgroup_path, "r", encoding="utf-8") as cgroup_file:
                cgroup_data = cgroup_file.read()
            return any(tag in cgroup_data for tag in ("docker", "containerd", "kubepods"))
        except OSError:
            return False

    return False


def _iris_process_running():
    try:
        result = subprocess.run(
            ["ps", "-eo", "args="],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return False

    if result.returncode != 0:
        return False

    process_list = result.stdout.lower()
    return "irisdb" in process_list or "intersystems iris" in process_list


def _build_health_data():
    now_local = datetime.now().astimezone()
    now_utc = datetime.now(timezone.utc)

    return {
        "status": "ok",
        "docker": {
            "running_in_container": _running_in_docker(),
            "container_hostname": os.getenv("HOSTNAME", "unknown"),
        },
        "iris": {
            "irissys": os.getenv("IRISSYS", "not-set"),
            "iris_executable": shutil.which("iris") or "not-found",
            "iris_process_running": _iris_process_running(),
        },
        "process": {
            "pid": os.getpid(),
            "uptime_seconds": round(time.time() - PROCESS_START_TS, 2),
            "date_local": now_local.date().isoformat(),
            "time_local": now_local.time().isoformat(timespec="seconds"),
            "datetime_utc": now_utc.isoformat(timespec="seconds"),
        },
    }


@app.route("/")
def index():
    return render_template(
        "index.html",
        endpoints=[
            {
                "path": url_for("server_variables"),
                "description": "Pantalla con variables del servidor",
            },
            {
                "path": url_for("health"),
                "description": "API JSON de salud para monitoreo",
            },
        ],
    )


@app.route("/health")
def health():
    return jsonify(_build_health_data())


@app.route("/server")
def server_variables():
    return render_template("server.html", data=_build_health_data())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
    