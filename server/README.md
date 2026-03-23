# Room Sensor Server

This server accepts JSON readings from one or more ESP32 devices and shows the latest reading from each device in a browser.

It accepts Fahrenheit or Celsius input and stores both.

## Endpoints

- `POST /api/readings`
- `POST /post`
- `GET /`
- `GET /api/readings/latest`
- `GET /api/readings/latest-by-device`
- `GET /api/readings`
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

Then open:

```text
http://localhost:6969/
```

The page displays timestamps in `US/Eastern` by default.

If your ESP32 is posting from another device on the LAN, point it at your computer's LAN IP on port `6969`.

## Local test with curl

```sh
curl -X POST http://127.0.0.1:6969/api/readings \
  -H "Content-Type: application/json" \
  -d '{"device_id":"test-esp32","temp_f":73.4,"humidity":50}'
```

The latest reading is persisted to `server/data/readings.jsonl` via the mounted Docker volume.
