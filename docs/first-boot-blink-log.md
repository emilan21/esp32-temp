# First Boot, Blink, and Log Exercise

This is a very small first exercise for this repo.

The goal is not to build the final room sensor yet. The goal is to get comfortable with the basic embedded loop:

1. edit code
2. build firmware
3. flash board
4. read logs
5. make one small change

## What you are trying to prove

By the end of this exercise, you want to know these three things:

- your ESP32 can boot your code
- your serial monitor shows your logs
- your firmware can toggle a GPIO on a timer

That is a strong enough base to move on to Wi-Fi and sensors.

## Exercise 1: Boot and log

Start with the smallest possible success.

Update `main/esp32-temp.c` so `app_main()` does only two things:

- define a log tag
- print a boot message

Shape to aim for:

```c
#include "esp_log.h"

static const char *TAG = "esp32_temp";

void app_main(void)
{
    ESP_LOGI(TAG, "boot ok");
}
```

Then run:

```sh
idf.py build
idf.py flash monitor
```

Success looks like:

- build completes
- flash completes
- monitor opens
- you see your `boot ok` log line

If this does not work yet, do not move on.

## Exercise 2: Repeating log message

Once one boot log works, add a repeating loop so you can see that your firmware keeps running.

Shape to aim for:

```c
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

static const char *TAG = "esp32_temp";

void app_main(void)
{
    while (1) {
        ESP_LOGI(TAG, "alive");
        vTaskDelay(pdMS_TO_TICKS(2000));
    }
}
```

What this teaches you:

- embedded code often runs forever
- delays are usually explicit
- serial logs are your feedback loop

## Exercise 3: Blink an LED

Now make one GPIO toggle on and off every second.

You will need to:

- choose a safe output GPIO for your board
- configure it as output
- set level high and low in a loop
- delay between changes

Use ESP-IDF docs/examples for:

- `driver/gpio.h`
- `gpio_config_t`
- `gpio_set_level()`

Keep the first version simple:

- no abstraction yet
- one GPIO only
- one loop only
- log each state change

Your logs might look like:

- `LED on`
- `LED off`

## Picking the LED pin

This part depends on your exact board.

Important note:

- some ESP32 dev boards have a built-in LED
- some do not
- the built-in LED pin is not always the same between boards

If you are not sure, check your board documentation first.

If there is no built-in LED, use:

- one GPIO output pin
- one external LED
- one resistor in series

## Suggested development rhythm

For each tiny change:

1. edit in Vim
2. run `idf.py build`
3. run `idf.py flash monitor`
4. watch logs
5. change only one thing if it fails

Do not change code, wiring, and config all at once.

## Common beginner mistakes in this exercise

- using the wrong serial port
- choosing a bad GPIO for output
- forgetting the LED resistor when using an external LED
- assuming the code is broken when the board wiring is wrong
- changing too much before testing

## Good checkpoints before moving on

Move to the next stage only when you can do all of these reliably:

- flash the board without confusion
- open the serial monitor and recognize your own logs
- explain what `app_main()` is doing
- blink an LED on a timer

## After this exercise

Once this is working, the next good order is:

1. Wi-Fi connect and log IP address
2. send a simple HTTP request
3. read DHT11 and print values
4. combine the sensor and network pieces

That keeps the project understandable and avoids debugging too many unknowns at once.
