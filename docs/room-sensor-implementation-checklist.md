# Room Sensor Implementation Checklist

This checklist ties the earlier milestone docs together into one path for this repo.

It is meant to help you build the full project yourself in C with Vim and `idf.py`, without jumping ahead too quickly.

## Goal

Build an ESP32 app that:

- reads room temperature and humidity from a DHT11
- connects to Wi‑Fi
- sends readings to a server over HTTP
- repeats on a fixed interval

## Repo starting point

Right now your project is very small:

- `main/esp32-temp.c`
- `main/CMakeLists.txt`
- project root `CMakeLists.txt`

That is a good beginner starting point.

You can keep the early version in `main/esp32-temp.c` only, then split files later if it starts getting crowded.

## Recommended build order

Follow this order and do not skip steps:

1. boot log works
2. repeating log works
3. LED blink works
4. Wi‑Fi connection works
5. HTTP request with dummy JSON works
6. DHT11 read and serial log works
7. real DHT11 values are sent over HTTP
8. retries and cleanup improve reliability

This order keeps failures isolated.

## Step 1: Boot and serial logs

Read first:

- `docs/esp-idf-concepts.md`
- `docs/first-boot-blink-log.md`

Checkpoint:

- `idf.py build flash monitor` works
- you see your own `ESP_LOGI()` messages

Do not move on until this feels routine.

## Step 2: Wi-Fi only

Read first:

- `docs/wifi-first-milestone.md`

Implementation target:

- initialize NVS
- initialize netif and event loop
- configure station mode
- connect to your AP
- log assigned IP

Checkpoint:

- reflash and reconnect reliably
- logs clearly show startup and connection events

## Step 3: HTTP with dummy data

Read first:

- `docs/http-first-milestone.md`

Implementation target:

- create a helper like `send_reading_http()`
- POST fixed JSON to a test endpoint
- log status code and failures

Checkpoint:

- your server or test endpoint receives the request
- logs show clear request success or failure

## Step 4: DHT11 only

Read first:

- `docs/dht11-first-milestone.md`

Implementation target:

- wire the DHT11 correctly
- choose one GPIO for data
- read the sensor at a safe interval
- verify checksum
- log `temp_c` and `humidity`

Checkpoint:

- values look plausible
- multiple reads succeed in a row

## Step 5: Combine HTTP and DHT11

Once steps 3 and 4 both work independently, combine them.

Implementation target:

- connect Wi‑Fi once at startup
- read DHT11 on a timer
- format one JSON payload using real values
- POST that payload to your server
- log both sensor and network outcomes

Suggested flow:

```text
app_main()
  -> init system pieces
  -> connect Wi-Fi
  -> start main loop or task

main loop/task
  -> read DHT11
  -> validate checksum/result
  -> build JSON payload
  -> send HTTP POST
  -> wait fixed interval
```

Checkpoint:

- server receives real temperature/humidity readings
- logs make it obvious whether failure is sensor-side or network-side

## Step 6: Move config out of source

Once the full path works, clean up configuration.

Good values to move into `menuconfig`:

- Wi‑Fi SSID
- Wi‑Fi password
- server URL
- device ID
- DHT11 GPIO
- upload interval seconds

Checkpoint:

- you can change environment-specific values without editing source code

## Step 7: Improve reliability

After the first end-to-end version works, improve behavior when things go wrong.

Good upgrades:

- retry Wi‑Fi connection when disconnected
- skip HTTP send if the sensor read failed
- log useful error codes
- avoid polling the DHT11 too quickly
- wait and try again if the server is down

Checkpoint:

- the device keeps running even when Wi‑Fi or server access is unstable

## Suggested file layout later

You do not need this on day one, but once `main/esp32-temp.c` feels too busy, a simple split would be:

- `main/esp32-temp.c` - app coordination
- `main/wifi.c` and `main/wifi.h` - station mode setup
- `main/http_client.c` and `main/http_client.h` - POST helper
- `main/dht11.c` and `main/dht11.h` - sensor reads

Keep it boring and obvious.

## Suggested data payload

Start with something tiny and stable:

```json
{
  "device_id": "room-1",
  "temp_c": 23,
  "humidity": 51
}
```

That is enough for a first version.

## Suggested coding habits for this repo

- add logs before and after important operations
- check `esp_err_t` returns
- make one change at a time
- keep notes on what worked
- use one milestone per session when possible

## Common failure categories

When something breaks, sort it into one of these buckets first:

- build error
- flash/serial issue
- Wi‑Fi setup issue
- HTTP/server issue
- sensor wiring or timing issue

That will usually tell you what doc to return to.

## Suggested working order for the docs

Use the docs in this sequence:

1. `docs/esp-idf-concepts.md`
2. `docs/vim-esp-idf-workflow.md`
3. `docs/first-boot-blink-log.md`
4. `docs/wifi-first-milestone.md`
5. `docs/http-first-milestone.md`
6. `docs/dht11-first-milestone.md`
7. `docs/room-sensor-implementation-checklist.md`

## Definition of done for version 1

Version 1 is done when:

- the ESP32 boots consistently
- Wi‑Fi connects without manual fiddling
- the DHT11 gives plausible readings
- the server receives those readings over HTTP
- logs are clear enough that future debugging will be easier

That is a strong first embedded project.
