# ESP32 Room Sensor

ESP-IDF project for reading temperature and humidity from a DHT11 on an ESP32 and posting the data over Wi-Fi to a local Flask server.

## What It Does

- reads a DHT11 from a configurable GPIO
- connects to Wi-Fi with ESP-IDF
- posts the latest successful reading to a local HTTP server
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

The firmware reads the sensor on a fixed interval and posts the latest successful reading every `POST_EVERY_N_READS` loop iterations. Its counter begins at zero, so the first successful reading is posted immediately. The current code does not average readings. Failed HTTP responses are not reliably treated as failures by the firmware; confirm receipt on the server while testing hardware.

The declared target is `esp32` (`dependencies.lock` and local `sdkconfig`), with ESP-IDF 5.5.3 recorded in `dependencies.lock`. The DHT driver and its helper library are also vendored under `managed_components/`; the lock file records their registry versions. Install and export a matching ESP-IDF toolchain before running `idf.py`. A clean checkout can create its own local `sdkconfig` with `idf.py set-target esp32` and `idf.py menuconfig`; never copy real Wi-Fi settings into tracked files.

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

If you want a different port:

```sh
SERVER_PORT=8090 docker compose up --build
```

Then open:

```text
http://localhost:8080/
```

History view:

```text
http://localhost:8080/history
```

## Build And Flash Firmware

```sh
idf.py set-target esp32
idf.py menuconfig
idf.py build
```

For multiple boards, set a different `DEVICE_ID` in `menuconfig` before flashing each one.

Examples: `living-room`, `bedroom`, and `office`.

`make build` is a shortcut for `idf.py build` after the ESP-IDF environment is exported. Build writes `build/`, `sdkconfig`, and generated component metadata. The application, bootloader, and partition binaries are under `build/`; they are generated outputs, not source. Keep local copies when needed for recovery. This repository does not publish firmware releases automatically.

Flashing and serial monitoring require a connected board and a deliberately selected port. After verifying GPIO wiring, Wi-Fi destination, and the intended board, an operator can run `idf.py -p /dev/ttyUSB0 flash monitor`. This is a manual hardware step; `make check` and CI never flash. Verify boot, DHT11 reads, Wi-Fi connection, and a corresponding server record. The local ESP-IDF toolchain may be unavailable on a general workstation.

## Checks

Install the server's declared Python dependencies in a disposable environment, then run lint, formatting, syntax, and server tests:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
make check
```

The tests use a temporary SQLite database and Flask's test client. They do not contact sensors, Wi-Fi, or the running server. `make build` is a separate firmware compile check. A successful software check does not establish board wiring, sensor accuracy, serial behavior, or network delivery.

## PCB and generated files

The KiCad board, schematic, project file, and symbol library under `pcb/esp32-temp/` are authored project inputs. The tracked backup ZIP, project-local settings, and lock files are historical artifacts retained for recovery; review them before any cleanup. KiCad's `.history/` is local editor history, preserved on the Arch workstation and in the batch-37/batch-38 recovery archives. It is ignored in new commits because it has no standalone upstream. A fresh checkout will not include those local snapshots.

The PCB material is a prototype, not a verified manufacturing release. KiCad ERC currently reports no issues, while PCB DRC reports an invalid board outline because no `Edge.Cuts` edges exist. Firmware and PCB changes should be checked together for GPIO and DHT11 wiring before fabrication or flashing.

## Hosting

Private Gitea `emilan/esp32-temp` is the authoritative upstream and pushes to the public GitHub `emilan21/esp32-temp` mirror. A nondeploying server-check workflow is configured for Gitea pushes and pull requests; hosted execution has not yet been observed. There is no automated flash, deployment, or release job. Keep Wi-Fi credentials in local ignored `sdkconfig` only.

## Docs

Beginner-oriented notes and milestone docs live in:

- `docs/index.md`

## Repository Notes

- `sdkconfig` should stay local to your machine and should not be published with real Wi-Fi credentials or local IPs
- server data is stored under `server/data/` and is ignored by git
- managed ESP-IDF components are currently checked into the repo under `managed_components/`
- no root project license is declared; the vendored components carry their own licenses

## Good Next Steps

- flash the remaining ESP32 boards with unique device ids
- run the nodes in different rooms and watch the dashboard
- move stable prototypes from breadboard to perfboard
- later, replace DHT11 with a more accurate sensor if needed
