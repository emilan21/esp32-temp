# ESP32 Temp Project Docs

This folder is a beginner-friendly guide for building your ESP32 + DHT11 room sensor project with C, Vim, and `idf.py`.

## Recommended reading order

1. `docs/esp-idf-concepts.md`
   - first 5 ESP-IDF ideas to understand before doing much coding

2. `docs/vim-esp-idf-workflow.md`
   - practical terminal workflow for editing, building, flashing, and monitoring

3. `docs/first-boot-blink-log.md`
   - first hands-on exercise: boot logs, repeating logs, and LED blink

4. `docs/wifi-first-milestone.md`
   - connect the ESP32 to Wi‑Fi and log the connection lifecycle

5. `docs/http-first-milestone.md`
   - send one HTTP request with dummy JSON data

6. `docs/dht11-first-milestone.md`
   - read the DHT11 and print valid values to the serial logs

7. `docs/room-sensor-implementation-checklist.md`
   - full project roadmap tying all milestones together for this repo

8. `docs/esp32-reading-list.md`
   - focused reading path so you only learn what you need next

## Suggested workflow

- keep `docs/room-sensor-implementation-checklist.md` open as your roadmap
- work through one milestone at a time in `main/esp32-temp.c`
- use `idf.py build flash monitor` as your main test loop
- do not combine Wi‑Fi, HTTP, and DHT11 until each one works alone

## Current project goal

Build an ESP32 app that:

- reads temperature and humidity from a DHT11
- connects to Wi‑Fi
- sends readings to a server over HTTP
- repeats on a fixed interval

## Good rule for learning embedded

When something breaks, reduce scope.

- make one small change
- test it immediately
- use logs heavily
- separate hardware problems from software problems

That approach will save you a lot of time.
