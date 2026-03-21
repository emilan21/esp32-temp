# Wi-Fi First Milestone

This exercise comes after `docs/first-boot-blink-log.md`.

The goal is simple: get your ESP32 onto your Wi‑Fi network and print enough logs to prove it worked.

Do not combine this with DHT11 or HTTP yet.

## What you are trying to prove

By the end of this exercise, you want to know these things:

- your ESP32 can initialize the network stack
- it can connect to your router in station mode
- it gets an IP address
- you can recognize the connection lifecycle in logs

## Why Wi-Fi should be its own step

If you try to learn Wi‑Fi, sensor timing, and HTTP all at once, debugging gets messy fast.

Wi‑Fi alone already introduces:

- startup ordering
- configuration
- async events
- reconnect behavior

Getting this stable first makes the rest of the project much easier.

## What to read first

Before writing code, read one official ESP-IDF station-mode example and look for:

- NVS initialization
- `esp_netif_init()`
- event loop creation
- Wi‑Fi init config
- station credentials setup
- event handler registration
- how IP acquisition is logged

You are not trying to memorize it. You are trying to understand the shape.

## First milestone behavior

Your first Wi‑Fi version should do only this:

1. boot
2. initialize Wi‑Fi
3. try to connect
4. log success or failure
5. keep running

That is enough.

## Configuration approach

Use `idf.py menuconfig` for Wi‑Fi credentials instead of hardcoding them if you can.

Good values to configure there:

- SSID
- password
- maybe a hostname later

If that feels like too much on day one, hardcoding for a temporary experiment is acceptable, but move to config soon after.

## Code shape to aim for

Do not copy this blindly. Use it as a mental model.

Your code will likely need these parts:

- a log tag
- a Wi‑Fi init function such as `wifi_init_sta()`
- one or more event handlers
- a way to wait until connected or failed
- `app_main()` calling Wi‑Fi setup

The flow usually looks like:

```text
app_main()
  -> init NVS
  -> init esp-netif
  -> create default event loop
  -> configure Wi-Fi in station mode
  -> register event handlers
  -> start Wi-Fi
  -> attempt connect
  -> log events
```

## Logs you want to see

Add enough logs that you can tell exactly where it fails.

Useful checkpoints:

- `boot ok`
- `initializing wifi`
- `wifi started`
- `connecting to ap`
- `got ip: ...`
- `retrying wifi`
- `wifi connect failed`

If all you print is one final success line, debugging will be harder.

## Keep the first version minimal

For the first milestone, you do not need:

- HTTP requests
- sensor reads
- JSON
- device provisioning
- fancy reconnect logic

You only need a clean connection flow.

## What success looks like

You know the milestone is done when:

- the board boots reliably
- logs show Wi‑Fi startup clearly
- the ESP32 joins your router
- you can see an IP address in logs
- reflashing and retesting feel repeatable, not lucky

## Common beginner problems

- wrong SSID or password
- 5 GHz network confusion if your setup expects 2.4 GHz
- not initializing NVS before Wi‑Fi setup
- missing event loop or handler registration
- not checking return codes
- too few logs to tell where startup stopped

## A simple debugging order

If it does not connect, check in this order:

1. credentials
2. router supports the device setup you expect
3. NVS and network init are happening
4. Wi‑Fi start is succeeding
5. events are being handled and logged

Do not jump straight into random code edits.

## Nice-to-have next step after connection works

Once Wi‑Fi is stable, the next milestone should be one simple HTTP request with dummy data.

That keeps the next problem narrow:

- if Wi‑Fi breaks, it is a Wi‑Fi problem
- if HTTP breaks, it is an HTTP problem

## Suggested checkpoint note

When this milestone works, write down:

- which example you used as a reference
- where your SSID/password are configured
- what successful logs look like
- what command you use most often, probably `idf.py flash monitor`

That note will save you time when you return to the project later.
