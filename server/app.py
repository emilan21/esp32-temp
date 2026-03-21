import json
import os
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, render_template, request


DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
DATA_FILE = DATA_DIR / "readings.jsonl"
RECENT_LIMIT = 20

app = Flask(__name__)


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


def parse_number(value, field_name):
    if isinstance(value, (int, float)):
        return value

    if isinstance(value, str):
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError as exc:
            raise ValueError(f"{field_name} must be numeric") from exc

    raise ValueError(f"{field_name} must be numeric")


def normalize_reading(payload):
    if not isinstance(payload, dict):
        raise ValueError("JSON body must be an object")

    if "temp_c" not in payload:
        raise ValueError("temp_c is required")

    if "humidity" not in payload:
        raise ValueError("humidity is required")

    device_id = str(payload.get("device_id", "unknown"))
    temp_c = parse_number(payload["temp_c"], "temp_c")
    humidity = parse_number(payload["humidity"], "humidity")

    reading = {
        "device_id": device_id,
        "temp_c": temp_c,
        "humidity": humidity,
        "received_at": utc_now_iso(),
    }

    if "sensor_timestamp" in payload:
        reading["sensor_timestamp"] = str(payload["sensor_timestamp"])

    return reading


def append_reading(reading):
    ensure_data_dir()
    with DATA_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(reading) + "\n")


def load_recent_readings(limit=RECENT_LIMIT):
    if not DATA_FILE.exists():
        return []

    readings = []
    with DATA_FILE.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                readings.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return list(reversed(readings[-limit:]))


def load_latest_reading():
    readings = load_recent_readings(limit=1)
    if not readings:
        return None
    return readings[0]


@app.get("/")
def index():
    latest = load_latest_reading()
    recent = load_recent_readings()
    return render_template("index.html", latest=latest, recent=recent)


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/readings/latest")
def latest_reading():
    latest = load_latest_reading()
    if latest is None:
        return jsonify({"message": "no readings yet"}), 404
    return jsonify(latest)


@app.get("/api/readings")
def recent_readings():
    return jsonify(load_recent_readings())


@app.post("/post")
@app.post("/api/readings")
def create_reading():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "request body must be valid JSON"}), 400

    try:
        reading = normalize_reading(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    append_reading(reading)
    return jsonify({"status": "ok", "reading": reading}), 200


if __name__ == "__main__":
    ensure_data_dir()
    port = int(os.environ.get("PORT", "6969"))
    app.run(host="0.0.0.0", port=port, debug=False)
