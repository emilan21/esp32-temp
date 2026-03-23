import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from flask import Flask, jsonify, render_template, request


DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
DB_FILE = DATA_DIR / "readings.db"
LEGACY_DATA_FILE = DATA_DIR / "readings.jsonl"
RECENT_LIMIT = 20
DISPLAY_TZ = ZoneInfo(os.environ.get("DISPLAY_TZ", "America/New_York"))
ALLOWED_RANGES = {
    "24h": timedelta(hours=24),
    "7d": timedelta(days=7),
    "30d": timedelta(days=30),
}
RANGE_BUCKET_SECONDS = {
    "24h": 300,
    "7d": 3600,
    "30d": 21600,
}
STALE_AFTER_MINUTES = int(os.environ.get("STALE_AFTER_MINUTES", "10"))
OFFLINE_AFTER_MINUTES = int(os.environ.get("OFFLINE_AFTER_MINUTES", "30"))

app = Flask(__name__)


@app.template_filter("local_time")
def local_time_filter(value):
    if not value:
        return "-"

    timestamp = datetime.fromisoformat(value)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    local_time = timestamp.astimezone(DISPLAY_TZ)
    formatted = local_time.strftime("%b %d, %Y %I:%M:%S %p %Z")
    return formatted.replace(" 0", " ")


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def utc_now():
    return datetime.now(timezone.utc)


def utc_now_iso():
    return utc_now().isoformat()


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


def c_to_f(temp_c):
    return (temp_c * 9.0 / 5.0) + 32.0


def f_to_c(temp_f):
    return (temp_f - 32.0) * 5.0 / 9.0


def parse_timestamp(value):
    if not value:
        return utc_now()

    timestamp = datetime.fromisoformat(value)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    return timestamp.astimezone(timezone.utc)


def normalize_reading(payload):
    if not isinstance(payload, dict):
        raise ValueError("JSON body must be an object")

    if "temp_f" not in payload and "temp_c" not in payload:
        raise ValueError("temp_f or temp_c is required")

    if "humidity" not in payload:
        raise ValueError("humidity is required")

    device_id = str(payload.get("device_id", "unknown")).strip() or "unknown"
    humidity = parse_number(payload["humidity"], "humidity")

    if "temp_f" in payload:
        temp_f = parse_number(payload["temp_f"], "temp_f")
        temp_c = round(f_to_c(temp_f), 2)
    else:
        temp_c = parse_number(payload["temp_c"], "temp_c")
        temp_f = round(c_to_f(temp_c), 2)

    sensor_time = payload.get("sensor_timestamp")
    reading = {
        "device_id": device_id,
        "temp_f": round(float(temp_f), 2),
        "temp_c": round(float(temp_c), 2),
        "humidity": round(float(humidity), 2),
        "sensor_timestamp": str(sensor_time) if sensor_time else None,
        "received_at": utc_now_iso(),
    }
    return reading


def init_db():
    ensure_data_dir()
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                temp_f REAL NOT NULL,
                temp_c REAL NOT NULL,
                humidity REAL NOT NULL,
                sensor_timestamp TEXT,
                received_at TEXT NOT NULL,
                received_at_ts INTEGER NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_readings_device_time ON readings(device_id, received_at_ts)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_readings_time ON readings(received_at_ts)"
        )
        conn.commit()


def migrate_legacy_jsonl_if_needed():
    if not LEGACY_DATA_FILE.exists():
        return

    with get_db_connection() as conn:
        existing = conn.execute("SELECT COUNT(*) AS count FROM readings").fetchone()[
            "count"
        ]
        if existing:
            return

        migrated = 0
        with LEGACY_DATA_FILE.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                    reading = normalize_reading(payload)
                    if payload.get("received_at"):
                        reading["received_at"] = parse_timestamp(
                            payload["received_at"]
                        ).isoformat()
                except (json.JSONDecodeError, ValueError):
                    continue

                received_at = parse_timestamp(reading["received_at"])
                conn.execute(
                    """
                    INSERT INTO readings (
                        device_id, temp_f, temp_c, humidity, sensor_timestamp,
                        received_at, received_at_ts
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        reading["device_id"],
                        reading["temp_f"],
                        reading["temp_c"],
                        reading["humidity"],
                        reading["sensor_timestamp"],
                        received_at.isoformat(),
                        int(received_at.timestamp()),
                    ),
                )
                migrated += 1
        conn.commit()
        if migrated:
            app.logger.info("Migrated %d legacy readings into SQLite", migrated)


def row_to_reading(row):
    if row is None:
        return None

    return {
        "id": row["id"],
        "device_id": row["device_id"],
        "temp_f": row["temp_f"],
        "temp_c": row["temp_c"],
        "humidity": row["humidity"],
        "sensor_timestamp": row["sensor_timestamp"],
        "received_at": row["received_at"],
    }


def describe_age(delta):
    seconds = max(int(delta.total_seconds()), 0)
    if seconds < 60:
        return "just now"

    minutes = seconds // 60
    if minutes < 60:
        unit = "minute" if minutes == 1 else "minutes"
        return f"{minutes} {unit} ago"

    hours = minutes // 60
    if hours < 24:
        unit = "hour" if hours == 1 else "hours"
        return f"{hours} {unit} ago"

    days = hours // 24
    unit = "day" if days == 1 else "days"
    return f"{days} {unit} ago"


def enrich_reading_status(reading):
    if not reading:
        return None

    received_at = parse_timestamp(reading["received_at"])
    age = utc_now() - received_at
    age_minutes = max(int(age.total_seconds() // 60), 0)

    if age_minutes >= OFFLINE_AFTER_MINUTES:
        status = "offline"
    elif age_minutes >= STALE_AFTER_MINUTES:
        status = "stale"
    else:
        status = "online"

    enriched = dict(reading)
    enriched["status"] = status
    enriched["age_minutes"] = age_minutes
    enriched["age_label"] = describe_age(age)
    return enriched


def summarize_device_statuses(devices):
    summary = {"online": 0, "stale": 0, "offline": 0}
    for device in devices:
        summary[device["status"]] += 1
    return summary


def append_reading(reading):
    received_at = parse_timestamp(reading["received_at"])
    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO readings (
                device_id, temp_f, temp_c, humidity, sensor_timestamp,
                received_at, received_at_ts
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                reading["device_id"],
                reading["temp_f"],
                reading["temp_c"],
                reading["humidity"],
                reading["sensor_timestamp"],
                received_at.isoformat(),
                int(received_at.timestamp()),
            ),
        )
        conn.commit()


def load_recent_readings(limit=RECENT_LIMIT):
    with get_db_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM readings
            ORDER BY received_at_ts DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [row_to_reading(row) for row in rows]


def load_latest_reading():
    with get_db_connection() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM readings
            ORDER BY received_at_ts DESC, id DESC
            LIMIT 1
            """
        ).fetchone()
    return row_to_reading(row)


def load_latest_by_device():
    with get_db_connection() as conn:
        rows = conn.execute(
            """
            SELECT r1.*
            FROM readings r1
            JOIN (
                SELECT device_id, MAX(received_at_ts) AS max_ts
                FROM readings
                GROUP BY device_id
            ) latest
              ON latest.device_id = r1.device_id
             AND latest.max_ts = r1.received_at_ts
            ORDER BY LOWER(r1.device_id), r1.id DESC
            """
        ).fetchall()

    seen = set()
    devices = []
    for row in rows:
        if row["device_id"] in seen:
            continue
        seen.add(row["device_id"])
        devices.append(enrich_reading_status(row_to_reading(row)))
    return devices


def load_device_ids():
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT DISTINCT device_id FROM readings ORDER BY LOWER(device_id)"
        ).fetchall()
    return [row["device_id"] for row in rows]


def resolve_range(range_name):
    return ALLOWED_RANGES.get(range_name, ALLOWED_RANGES["24h"])


def resolve_bucket_seconds(range_name):
    return RANGE_BUCKET_SECONDS.get(range_name, RANGE_BUCKET_SECONDS["24h"])


def load_history(device_id, range_name):
    cutoff = utc_now() - resolve_range(range_name)
    bucket_seconds = resolve_bucket_seconds(range_name)
    cutoff_ts = int(cutoff.timestamp())

    with get_db_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                MIN(id) AS id,
                device_id,
                AVG(temp_f) AS temp_f,
                AVG(temp_c) AS temp_c,
                AVG(humidity) AS humidity,
                MIN(sensor_timestamp) AS sensor_timestamp,
                MIN(received_at_ts) AS received_at_ts
            FROM readings
            WHERE device_id = ?
              AND received_at_ts >= ?
            GROUP BY device_id, (received_at_ts / ?)
            ORDER BY received_at_ts ASC
            """,
            (device_id, cutoff_ts, bucket_seconds),
        ).fetchall()

    points = []
    for row in rows:
        timestamp = datetime.fromtimestamp(
            row["received_at_ts"], tz=timezone.utc
        ).isoformat()
        points.append(
            {
                "id": row["id"],
                "device_id": row["device_id"],
                "temp_f": round(row["temp_f"], 2),
                "temp_c": round(row["temp_c"], 2),
                "humidity": round(row["humidity"], 2),
                "sensor_timestamp": row["sensor_timestamp"],
                "received_at": timestamp,
            }
        )
    return points


def summarize_history(points):
    if not points:
        return None

    temps = [point["temp_f"] for point in points]
    humidity = [point["humidity"] for point in points]
    return {
        "count": len(points),
        "avg_temp_f": round(sum(temps) / len(temps), 2),
        "min_temp_f": round(min(temps), 2),
        "max_temp_f": round(max(temps), 2),
        "avg_humidity": round(sum(humidity) / len(humidity), 2),
        "min_humidity": round(min(humidity), 2),
        "max_humidity": round(max(humidity), 2),
    }


@app.get("/")
def index():
    latest = enrich_reading_status(load_latest_reading())
    devices = load_latest_by_device()
    recent = load_recent_readings()
    return render_template(
        "index.html",
        latest=latest,
        devices=devices,
        device_count=len(devices),
        status_summary=summarize_device_statuses(devices),
        recent=recent,
    )


@app.get("/history")
def history_page():
    device_ids = load_device_ids()
    selected_device = request.args.get("device_id", "")
    range_name = request.args.get("range", "24h")
    if range_name not in ALLOWED_RANGES:
        range_name = "24h"

    if not selected_device and device_ids:
        selected_device = device_ids[0]

    history = load_history(selected_device, range_name) if selected_device else []
    summary = summarize_history(history)
    return render_template(
        "history.html",
        device_ids=device_ids,
        selected_device=selected_device,
        selected_range=range_name,
        allowed_ranges=list(ALLOWED_RANGES.keys()),
        history=history,
        summary=summary,
    )


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/readings/latest")
def latest_reading():
    latest = enrich_reading_status(load_latest_reading())
    if latest is None:
        return jsonify({"message": "no readings yet"}), 404
    return jsonify(latest)


@app.get("/api/readings/latest-by-device")
def latest_readings_by_device():
    return jsonify(load_latest_by_device())


@app.get("/api/readings")
def recent_readings():
    return jsonify(load_recent_readings())


@app.get("/api/readings/history")
def reading_history():
    device_id = request.args.get("device_id", "").strip()
    if not device_id:
        return jsonify({"error": "device_id is required"}), 400

    range_name = request.args.get("range", "24h")
    if range_name not in ALLOWED_RANGES:
        return jsonify(
            {"error": f"range must be one of {', '.join(ALLOWED_RANGES.keys())}"}
        ), 400

    points = load_history(device_id, range_name)
    return jsonify(
        {
            "device_id": device_id,
            "range": range_name,
            "points": points,
            "summary": summarize_history(points),
        }
    )


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


init_db()
migrate_legacy_jsonl_if_needed()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=False)
