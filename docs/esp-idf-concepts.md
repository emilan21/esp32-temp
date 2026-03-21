# First 5 ESP-IDF Concepts

This is a beginner cheat sheet for working on this ESP32 project with C, Vim, and `idf.py`.

## 1. `app_main()` is your entry point

- ESP-IDF starts your application at `app_main()`.
- In this repo, that function currently lives in `main/esp32-temp.c`.
- A tiny first version looks like this:

```c
void app_main(void)
{
    // initialize things here
    // then start your main behavior
}
```

What to remember:

- There is usually no normal program exit.
- Embedded code often initializes hardware and then runs forever.
- Keep `app_main()` small once the project grows.

## 2. Components and project structure

ESP-IDF projects are organized into components.

In this repo you already have:

- `CMakeLists.txt` at the project root
- `main/CMakeLists.txt`
- `main/esp32-temp.c`

For a beginner, `main/` is enough.

Later, you can split code into files like:

- `main/wifi.c`
- `main/wifi.h`
- `main/dht11.c`
- `main/dht11.h`

Rule of thumb:

- put related code in a `.c` file
- expose only what other files need in a `.h` file
- do not split files until the code starts feeling crowded

## 3. Logging is your main debugging tool

On embedded targets, logs are often your fastest feedback loop.

Use ESP-IDF logging instead of only `printf`:

```c
#include "esp_log.h"

static const char *TAG = "room_sensor";

ESP_LOGI(TAG, "Boot ok");
ESP_LOGW(TAG, "Wi-Fi not connected yet");
ESP_LOGE(TAG, "DHT11 checksum failed");
```

Common log levels:

- `ESP_LOGI` for normal progress
- `ESP_LOGW` for recoverable problems
- `ESP_LOGE` for failures

Use logs around:

- Wi-Fi connect start and result
- sensor read attempts
- HTTP request start and response code
- retries and error paths

## 4. FreeRTOS tasks are lightweight threads

ESP-IDF runs on FreeRTOS.

You do not need to master RTOS concepts immediately, but you should know this pattern:

- initialize things in `app_main()`
- create a task for repeated work
- let the task loop forever with delays

Example shape:

```c
static void sensor_task(void *arg)
{
    while (1) {
        // read sensor
        // send network request
        vTaskDelay(pdMS_TO_TICKS(5000));
    }
}

void app_main(void)
{
    xTaskCreate(sensor_task, "sensor_task", 4096, NULL, 5, NULL);
}
```

Why this helps:

- it keeps repeated logic out of `app_main()`
- delays are explicit
- later you can separate Wi-Fi, sensor, and upload logic if needed

## 5. Configuration belongs in `menuconfig`

Avoid hardcoding values that change between setups.

Good candidates:

- Wi-Fi SSID
- Wi-Fi password
- server URL
- sensor GPIO number
- device name
- upload interval

Useful command:

```sh
idf.py menuconfig
```

Why this matters:

- your code stays cleaner
- you can reconfigure without editing source every time
- it matches normal ESP-IDF workflow

## Practical mental model

For your project, think in this order:

1. Boot
2. Initialize Wi-Fi
3. Read DHT11
4. Send result to server
5. Wait and repeat

If something breaks, debug in the same order.

## Best beginner habits

- make one small change at a time
- check return values
- log every major step
- test hardware pieces separately before combining them
- prefer simple C over clever C
