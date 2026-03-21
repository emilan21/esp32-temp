#include "driver/gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/projdefs.h"
#include "freertos/task.h"
#include "hal/gpio_types.h"
#include "sdkconfig.h"

#define STATUS_LED_GPIO CONFIG_STATUS_LED_GPIO
#define GPIO_OUTPUT_PIN_SEL ((1ULL << STATUS_LED_GPIO))

static const char *TAG = "esp32_temp";

void app_main(void) {
  gpio_config_t io_conf = {};
  io_conf.intr_type = GPIO_INTR_DISABLE;
  io_conf.mode = GPIO_MODE_OUTPUT;
  io_conf.pin_bit_mask = GPIO_OUTPUT_PIN_SEL;
  io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
  io_conf.pull_up_en = GPIO_PULLUP_DISABLE;
  gpio_config(&io_conf);

  int cnt = 0;
  while (1) {
    ESP_LOGI(TAG, "cnt: %d\n", cnt++);
    vTaskDelay(pdMS_TO_TICKS(1000));
    gpio_set_level(STATUS_LED_GPIO, cnt % 2);
  }
}
