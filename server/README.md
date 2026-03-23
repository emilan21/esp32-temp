# Room Sensor Server

This server accepts JSON readings from one or more ESP32 devices and shows the latest reading from each device in a browser.

It accepts Fahrenheit or Celsius input and stores both.

Readings are stored in SQLite so you can inspect history ranges like the last 24 hours or 7 days.

## Endpoints

- `POST /api/readings`
- `POST /post`
- `GET /`
- `GET /history`
- `GET /api/readings/latest`
- `GET /api/readings/latest-by-device`
- `GET /api/readings`
- `GET /api/readings/history?device_id=living-room&range=24h`
- `GET /health`

## Expected JSON

```json
{
  "device_id": "living-room",
  "temp_f": 73.4,
  "humidity": 51
}
```

`temp_c` also works if you prefer to send Celsius.

String numbers are accepted too, so your current ESP32 payload style will still work.

Use a unique `device_id` for each board so the dashboard can show one card per room.

## Run with Docker Compose

From the project root:

```sh
docker compose up --build
```

To use a different port:

```sh
SERVER_PORT=8090 docker compose up --build
```

Then open:

```text
http://localhost:8080/
```

The page displays timestamps in `US/Eastern` by default.

The history page supports these ranges:

- `24h`
- `7d`
- `30d`

If your ESP32 is posting from another device on the LAN, point it at your computer's LAN IP on whatever `SERVER_PORT` you chose.

## Local test with curl

```sh
curl -X POST http://127.0.0.1:8080/api/readings \
  -H "Content-Type: application/json" \
  -d '{"device_id":"test-esp32","temp_f":73.4,"humidity":50}'
```

The database is persisted to `server/data/readings.db` via the mounted Docker volume.

If an older `server/data/readings.jsonl` file exists, the server will import it into SQLite the first time it starts with an empty database.
