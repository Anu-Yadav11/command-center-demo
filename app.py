# app.py
from flask import Flask, jsonify, send_from_directory, request
import requests, os

app = Flask(__name__, static_folder="static", static_url_path="/")

PROM_URL = os.getenv("PROM_URL", "http://localhost:9090")
ALERTMANAGER_URL = os.getenv("ALERTMANAGER_URL", "http://localhost:9093")

# -------- Root & Static --------
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory("static", path)

# -------- Application Status --------
@app.route("/api/app")
def api_app():
    try:
        r = requests.get(f"{PROM_URL}/api/v1/query",
                         params={"query": 'up{job="node_exporter"}'}, timeout=5)
        r.raise_for_status()
        data = r.json()
        up = 1 if data["data"]["result"] and float(data["data"]["result"][0]["value"][1]) == 1 else 0
    except:
        up = 0
    return jsonify({"name": "App", "up": up})

# -------- Metrics (CPU/Disk) --------
@app.route("/api/metrics")
def api_metrics():
    try:
        cpu_q = '100 * (1 - avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])))'
        disk_q = '100 * (1 - node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})'
        r1 = requests.get(f"{PROM_URL}/api/v1/query", params={"query": cpu_q}, timeout=5).json()
        r2 = requests.get(f"{PROM_URL}/api/v1/query", params={"query": disk_q}, timeout=5).json()
        cpu = round(float(r1["data"]["result"][0]["value"][1]), 2) if r1["data"]["result"] else None
        disk = round(float(r2["data"]["result"][0]["value"][1]), 2) if r2["data"]["result"] else None
    except:
        cpu, disk = None, None
    return jsonify({"cpu_percent": cpu, "disk_percent": disk})

# -------- Alerts (for OPEN ALERTS column) --------
@app.route("/api/alerts")
def api_alerts():
    """Return Sev1/Sev2/Sev3 counts for Alerts column"""
    try:
        r = requests.get(f"{ALERTMANAGER_URL}/api/v2/alerts", timeout=5)
        r.raise_for_status()
        alerts = r.json()
    except Exception:
        return jsonify({"sev1": 0, "sev2": 0, "sev3": 0})

    sev_counts = {"sev1": 0, "sev2": 0, "sev3": 0}
    for alert in alerts:
        sev = alert["labels"].get("severity", "sev3").lower()
        if sev in sev_counts:
            sev_counts[sev] += 1

    return jsonify(sev_counts)

# -------- DT Problems (for OPEN PROBLEMS column) --------
@app.route("/api/dt_problems")
def api_dt_problems():
    try:
        r = requests.get(f"{ALERTMANAGER_URL}/api/v2/alerts", timeout=5)
        r.raise_for_status()
        alerts = r.json()
    except Exception as e:
        return jsonify({
            "auto": {"sev1": 0, "sev2": 0, "sev3": 0},
            "manual": {"sev1": [], "sev2": [], "sev3": []},
            "total": {"sev1": 0, "sev2": 0, "sev3": 0},
            "error": str(e)
        })

    auto = {"sev1": 0, "sev2": 0, "sev3": 0}
    manual = {"sev1": [], "sev2": [], "sev3": []}

    for alert in alerts:
        sev = alert["labels"].get("severity", "sev3").lower()
        if sev in auto:
            auto[sev] += 1
            manual[sev].append(
                alert.get("annotations", {}).get("summary", alert["labels"].get("alertname", "unknown"))
            )

    total = {
        "sev1": auto["sev1"] + len(manual["sev1"]),
        "sev2": auto["sev2"] + len(manual["sev2"]),
        "sev3": auto["sev3"] + len(manual["sev3"]),
    }

    return jsonify({"auto": auto, "manual": manual, "total": total})

# -------- Tickets (demo static) --------
@app.route("/api/tickets")
def api_tickets():
    return jsonify({"open_incidents": 1, "open_changes": 2})

# -------- Release Info (demo static) --------
@app.route("/api/release")
def api_release():
    return jsonify({"deployments_last_24h": 2, "db_changes_last_24h": 1})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

