# ESP32 Room Sensor

ESP-IDF project for reading temperature and humidity from a DHT11 on an ESP32 and posting the data over Wi-Fi to a local Flask server.

## What It Does

- reads a DHT11 from a configurable GPIO
- connects to Wi-Fi with ESP-IDF
- posts averaged readings to a local HTTP server
- shows live status and history on a small web dashboard
- supports multiple ESP32 nodes by using a unique `device_id` per board

## Hardware

- ESP32 dev board
- DHT11 module
- USB power

For a multi-room setup, the intended layout is one ESP32 plus one sensor per room.

## Firmware

Main firmware entry point:

- `main/esp32-temp.c`

Project config options are exposed through:

- `main/Kconfig.projbuild`

Important configurable values include:

- `DEVICE_ID`
- `DHT11_GPIO`
- `SENSOR_READ_INTERVAL_SECONDS`
- `POST_EVERY_N_READS`
- Wi-Fi SSID and password
- HTTP host, port, and path

The firmware reads the sensor on a fixed interval, averages the successful pulls, and posts the average after `POST_EVERY_N_READS` samples.

## Server

Server files live in:

- `server/app.py`
- `server/templates/index.html`
- `server/templates/history.html`

The server:

- accepts `POST /post` and `POST /api/readings`
- stores readings in SQLite
- shows a live multi-device dashboard at `/`
- shows time-range history at `/history`

## Run The Server

From the repo root:

```sh
docker compose up --build
```

Then open:

```text
http://localhost:6969/
```

History view:

```text
http://localhost:6969/history
```

## Build And Flash Firmware

```sh
idf.py menuconfig
idf.py build
idf.py flash monitor
```

For multiple boards, set a different `DEVICE_ID` in `menuconfig` before flashing each one.

Examples:

- `living-room`
- `bedroom`
- `office`

## Docs

Beginner-oriented notes and milestone docs live in:

- `docs/index.md`

## Repository Notes

- `sdkconfig` should stay local to your machine and should not be published with real Wi-Fi credentials or local IPs
- server data is stored under `server/data/` and is ignored by git
- managed ESP-IDF components are currently checked into the repo under `managed_components/`

## Good Next Steps

- flash the remaining ESP32 boards with unique device ids
- run the nodes in different rooms and watch the dashboard
- move stable prototypes from breadboard to perfboard
- later, replace DHT11 with a more accurate sensor if needed
