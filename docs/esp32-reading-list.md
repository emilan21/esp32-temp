# ESP32 Learning Reading List

This reading list is meant to keep you moving without drowning you in docs.

## Read in this order

### 1. ESP-IDF basics

Goal: understand how an app starts, builds, and logs.

Read about:

- project structure
- `app_main()`
- build/flash/monitor workflow
- logging

What you want after this stage:

- you can edit `main/esp32-temp.c`
- you can build and flash confidently
- you can recognize your own logs in serial output

### 2. GPIO and timing

Goal: understand how the ESP32 talks to simple hardware.

Read about:

- GPIO input/output configuration
- pull-up and pull-down basics
- delays and timing
- when busy timing is needed versus task delays

Why this matters:

- the DHT11 depends on pin control and timing
- many sensor issues are electrical or timing-related, not logic-related

### 3. FreeRTOS basics

Goal: understand how repeated work is normally structured.

Read about:

- tasks
- `vTaskDelay`
- stack size basics
- why code often runs forever in loops

You do not need queues, semaphores, or advanced scheduling on day one.

### 4. Wi-Fi station mode

Goal: get the ESP32 onto your network.

Read about:

- station mode initialization
- events and connection handling
- getting an IP address
- reconnect behavior

Practical outcome:

- your board joins your router and logs success

### 5. HTTP client

Goal: send data to your server.

Read about:

- `esp_http_client`
- HTTP GET versus POST
- request headers
- JSON request bodies
- response status handling

Practical outcome:

- send one dummy reading to a test endpoint

### 6. DHT11-specific material

Goal: understand the sensor's limits and protocol.

Read about:

- wiring diagram for your exact module
- pull-up resistor requirement
- 40-bit response structure
- checksum validation
- minimum polling interval

Important expectation:

- DHT11 is simple but not very accurate
- it is fine for learning, but not ideal for precise measurement

## Best sources to use

### Official ESP-IDF docs

Use official docs first for:

- APIs
- examples
- config options
- expected behavior

### ESP-IDF examples

These are some of the best learning material because they show working patterns.

Use examples for:

- Wi-Fi station mode
- HTTP client usage
- GPIO setup
- FreeRTOS task structure

When reading examples, look for:

- init order
- error handling style
- event handler patterns
- how config values are passed around

### Sensor docs and trusted example drivers

For the DHT11, it is normal to read:

- the sensor datasheet
- module pinout pages
- a known-good ESP-IDF-compatible driver for reference

If you borrow ideas, try to understand the timing and checksum logic rather than copying blindly.

## A practical reading strategy

Do not try to read everything first.

Use this rhythm:

1. pick the next small task
2. read only the docs needed for that task
3. implement a tiny version
4. test it on hardware
5. go back to the docs when the next question appears

Example:

- if the next task is Wi-Fi, read station mode docs and one example only
- if the next task is DHT11, read GPIO/timing docs and the sensor protocol only

## What to skip for now

Until your first version works, you can ignore:

- BLE
- OTA updates
- deep sleep
- advanced FreeRTOS synchronization
- custom partition layouts
- TLS internals
- performance tuning

Those are useful later, but they will slow down a beginner project.

## Suggested reading tied to your project

Follow this sequence:

1. ESP-IDF build/flash/monitor basics
2. logging and `app_main()`
3. GPIO basics
4. Wi-Fi station example
5. HTTP client example
6. DHT11 protocol notes
7. `menuconfig` basics

That sequence maps directly to the room sensor project you want to build.
