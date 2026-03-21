#include "dht.h"
#include "driver/gpio.h"
#include "esp_crt_bundle.h"
#include "esp_err.h"
#include "esp_event.h"
#include "esp_event_base.h"
#include "esp_http_client.h"
#include "esp_log.h"
#include "esp_log_buffer.h"
#include "esp_log_level.h"
#include "esp_netif.h"
#include "esp_netif_ip_addr.h"
#include "esp_netif_types.h"
#include "esp_system.h"
#include "esp_tls.h"
#include "esp_wifi.h"
#include "esp_wifi_default.h"
#include "esp_wifi_types_generic.h"
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "freertos/projdefs.h"
#include "freertos/task.h"
#include "hal/gpio_types.h"
#include "lwip/err.h"
#include "lwip/sys.h"
#include "nvs.h"
#include "nvs_flash.h"
#include "portmacro.h"
#include "sdkconfig.h"
#include <ctype.h>
#include <stdlib.h>
#include <string.h>
#include <sys/param.h>

// Logs
static const char *ESP32_GENERAL_TAG = "esp32_temp";
static const char *DHT11_TAG = "dht11";
static const char *WIFI_TAG = "wifi station";
static const char *HTTP_CLIENT_TAG = "HTTP_CLIENT";

// GPIO
#define STATUS_LED_GPIO CONFIG_STATUS_LED_GPIO
#define GPIO_OUTPUT_LED_SEL ((1ULL << STATUS_LED_GPIO))

// Wifi
#define ESP_WIFI_SSID CONFIG_ESP_WIFI_SSID
#define ESP_WIFI_PASSWORD CONFIG_ESP_WIFI_PASSWORD
#define ESP_WIFI_MAXIMUM_RETRY CONFIG_ESP_WIFI_MAXIMUM_RETRY

#if CONFIG_ESP_STATION_WPA3_SAE_PWE_HUNT_AND_PECK
#define ESP_WIFI_SAE_MODE WPA3_SAE_PWE_HUNT_AND_PECK
#define H2E_IDENTIFIER ""
#elif CONFIG_ESP_STATION_WPA3_SAE_PWE_HASH_TO_ELEMENT
#define ESP_WIFI_SAE_MODE WPA3_SAE_PWE_HASH_TO_ELEMENT
#define H2E_IDENTIFIER CONFIG_ESP_WIFI_PW_ID
#elif CONFIG_ESP_STATION_WPA3_SAE_PWE_BOTH
#define ESP_WIFI_SAE_MODE WPA3_SAE_PWE_BOTH
#define H2E_IDENTIFIER CONFIG_ESP_WIFI_PW_ID
#endif
#if CONFIG_ESP_WIFI_AUTH_OPEN
#define ESP_WIFI_SCAN_AUTH_MODE_THRESHOLD WIFI_AUTH_OPEN
#elif CONFIG_ESP_WIFI_AUTH_WEP
#define ESP_WIFI_SCAN_AUTH_MODE_THRESHOLD WIFI_AUTH_WEP
#elif CONFIG_ESP_WIFI_AUTH_WPA_PSK
#define ESP_WIFI_SCAN_AUTH_MODE_THRESHOLD WIFI_AUTH_WPA_PSK
#elif CONFIG_ESP_WIFI_AUTH_WPA2_PSK
#define ESP_WIFI_SCAN_AUTH_MODE_THRESHOLD WIFI_AUTH_WPA2_PSK
#elif CONFIG_ESP_WIFI_AUTH_WPA_WPA2_PSK
#define ESP_WIFI_SCAN_AUTH_MODE_THRESHOLD WIFI_AUTH_WPA_WPA2_PSK
#elif CONFIG_ESP_WIFI_AUTH_WPA3_PSK
#define ESP_WIFI_SCAN_AUTH_MODE_THRESHOLD WIFI_AUTH_WPA3_PSK
#elif CONFIG_ESP_WIFI_AUTH_WPA2_WPA3_PSK
#define ESP_WIFI_SCAN_AUTH_MODE_THRESHOLD WIFI_AUTH_WPA2_WPA3_PSK
#elif CONFIG_ESP_WIFI_AUTH_WAPI_PSK
#define ESP_WIFI_SCAN_AUTH_MODE_THRESHOLD WIFI_AUTH_WAPI_PSK
#endif

#define WIFI_CONNECTED_BIT BIT0
#define WIFI_FAIL_BIT BIT1
static EventGroupHandle_t s_wifi_event_group;
static int s_retry_num = 0;

static void event_handler(void *arg, esp_event_base_t event_base,
                          int32_t event_id, void *event_data) {
  if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
    esp_wifi_connect();
  } else if (event_base == WIFI_EVENT &&
             event_id == WIFI_EVENT_STA_DISCONNECTED) {
    if (s_retry_num < ESP_WIFI_MAXIMUM_RETRY) {
      esp_wifi_connect();
      s_retry_num++;
      ESP_LOGI(WIFI_TAG, "retry to connect to the AP");
    } else {
      xEventGroupSetBits(s_wifi_event_group, WIFI_FAIL_BIT);
    }
    ESP_LOGI(WIFI_TAG, "connect to the AP fail");
  } else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
    ip_event_got_ip_t *event = (ip_event_got_ip_t *)event_data;
    ESP_LOGI(WIFI_TAG, "got ip:" IPSTR, IP2STR(&event->ip_info.ip));
    s_retry_num = 0;
    xEventGroupSetBits(s_wifi_event_group, WIFI_CONNECTED_BIT);
  }
}

void wifi_init_sta(void) {
  s_wifi_event_group = xEventGroupCreate();

  ESP_ERROR_CHECK(esp_netif_init());

  ESP_ERROR_CHECK(esp_event_loop_create_default());
  esp_netif_create_default_wifi_sta();

  wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
  ESP_ERROR_CHECK(esp_wifi_init(&cfg));

  esp_event_handler_instance_t instance_any_id;
  esp_event_handler_instance_t instance_got_ip;
  ESP_ERROR_CHECK(esp_event_handler_instance_register(
      WIFI_EVENT, ESP_EVENT_ANY_ID, &event_handler, NULL, &instance_any_id));
  ESP_ERROR_CHECK(esp_event_handler_instance_register(
      IP_EVENT, IP_EVENT_STA_GOT_IP, &event_handler, NULL, &instance_got_ip));

  wifi_config_t wifi_config = {
      .sta =
          {
              .ssid = ESP_WIFI_SSID,
              .password = ESP_WIFI_PASSWORD,
              .threshold.authmode = ESP_WIFI_SCAN_AUTH_MODE_THRESHOLD,
              .sae_pwe_h2e = ESP_WIFI_SAE_MODE,
              .sae_h2e_identifier = H2E_IDENTIFIER,
#ifdef CONFIG_ESP_WIFI_WPA3_COMPATIBLE_SUPPORT
              .disable_wpa3_compatible_mode = 0,
#endif
          },
  };
  ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
  ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config));
  ESP_ERROR_CHECK(esp_wifi_start());

  ESP_LOGI(WIFI_TAG, "wifi_init_sta finshed");

  EventBits_t bits = xEventGroupWaitBits(s_wifi_event_group,
                                         WIFI_CONNECTED_BIT | WIFI_FAIL_BIT,
                                         pdFALSE, pdFALSE, portMAX_DELAY);

  if (bits & WIFI_CONNECTED_BIT) {
    ESP_LOGI(WIFI_TAG, "connected to ap SSID:%s password:%s", ESP_WIFI_SSID,
             ESP_WIFI_PASSWORD);
  } else if (bits & WIFI_FAIL_BIT) {
    ESP_LOGI(WIFI_TAG, "Falied to connect to SSID:%s, password:%s",
             ESP_WIFI_SSID, ESP_WIFI_PASSWORD);
  } else {
    ESP_LOGE(WIFI_TAG, "UNEXPECTED EVENT");
  }
}

// HTTP client
#define MAX_HTTP_RECV_BUFFER 512
#define MAX_HTTP_OUTPUT_BUFFER 2048

esp_err_t _http_event_handler(esp_http_client_event_t *evt) {
  static char *output_buffer;
  static int output_len;

  switch (evt->event_id) {
  case HTTP_EVENT_ERROR:
    ESP_LOGD(HTTP_CLIENT_TAG, "HTTP_EVENT_ERROR");
    break;
  case HTTP_EVENT_ON_CONNECTED:
    ESP_LOGD(HTTP_CLIENT_TAG, "HTTP_EVENT_ON_CONNECTED");
    break;
  case HTTP_EVENT_HEADER_SENT:
    ESP_LOGD(HTTP_CLIENT_TAG, "HTTP_EVENT_HEADER_SENT");
    break;
  case HTTP_EVENT_ON_HEADER:
    ESP_LOGD(HTTP_CLIENT_TAG, "HTTP_EVENT_ON_HEADER, key=%s, value=%s",
             evt->header_key, evt->header_value);
    break;
  // case HTTP_EVENT_ON_HEADERS_COMPLETE:
  //  ESP_LOGD(HTTP_CLIENT_TAG, "HTTP_EVENT_ON_HEADERS_COMPLETE");
  // break;
  case HTTP_EVENT_ON_DATA:
    ESP_LOGD(HTTP_CLIENT_TAG, "HTTP_EVENT_ON_DATA, len=%d", evt->data_len);
    // Clean the buffer in case of a new request
    if (output_len == 0 && evt->user_data) {
      // we are just starting to copy the output data into the use
      memset(evt->user_data, 0, MAX_HTTP_OUTPUT_BUFFER);
    }
    /*
     * Check for chunked encoding is added as the URL for chucked encoding used
     * in this example returns binary data. However, event handler can also be
     * used in case chunked encoding is used.
     */
    if (!esp_http_client_is_chunked_response(evt->client)) {
      // If user_data buffer is configured, copy the reponse into the buffer
      int copy_len = 0;
      if (evt->user_data) {
        // The last byte in evt->user_data is kept for NULL character in case of
        // out-of-bound access.
        copy_len = MIN(evt->data_len, (MAX_HTTP_OUTPUT_BUFFER - output_len));
        if (copy_len) {
          memcpy(evt->user_data + output_len, evt->data, copy_len);
        }
      } else {
        int content_len = esp_http_client_get_content_length(evt->client);
        if (output_buffer == NULL) {
          // We initialize output_buffer with 0 because it is used by strlen()
          // and simlar functions therefore should be null terminated.
          output_buffer = (char *)calloc(content_len + 1, sizeof(char));
          output_len = 0;
          if (output_buffer == NULL) {
            ESP_LOGE(HTTP_CLIENT_TAG,
                     "Failed to allocate memory for output buffer");
            return ESP_FAIL;
          }
        }
        copy_len = MIN(evt->data_len, (content_len - output_len));
        if (copy_len) {
          memcpy(output_buffer + output_len, evt->data, copy_len);
        }
      }
      output_len += copy_len;
    }
    break;
  case HTTP_EVENT_ON_FINISH:
    ESP_LOGD(HTTP_CLIENT_TAG, "HTTP_EVENT_ON_FINISH");
    if (output_buffer != NULL) {
#if CONFIG_ENABLE_REPONSE_BUFFER_DUMP
      ESP_LOG_BUFFER_HEX(HTTP_CLIENT_TAG, output_buffer, output_len);
#endif
      free(output_buffer);
      output_buffer = NULL;
    }
    output_len = 0;
    break;
  case HTTP_EVENT_DISCONNECTED:
    ESP_LOGI(HTTP_CLIENT_TAG, "HTTP_EVENT_DISCONNECTED");
    int mbedtls_err = 0;
    esp_err_t err = esp_tls_get_and_clear_last_error(
        (esp_tls_error_handle_t)evt->data, &mbedtls_err, NULL);
    if (err != 0) {
      ESP_LOGI(HTTP_CLIENT_TAG, "Last esp error code: 0x%x", err);
      ESP_LOGI(HTTP_CLIENT_TAG, "Last mbedtls failure: 0x%x", mbedtls_err);
    }
    if (output_buffer != NULL) {
      free(output_buffer);
      output_buffer = NULL;
    }
    output_len = 0;
    break;
  case HTTP_EVENT_REDIRECT:
    ESP_LOGD(HTTP_CLIENT_TAG, "HTTP_EVENT_REDIRECT");
    esp_http_client_set_header(evt->client, "From", "user@example.com");
    esp_http_client_set_header(evt->client, "Accept", "text/html");
    esp_http_client_set_redirection(evt->client);
    break;
  default:
    break;
  }
  return ESP_OK;
}

static void http_rest_with_url(void) {
  // Declare local_response_buffer with size (MAX_HTTP_OUTPUT_BUFFER + 1) to
  // prevent out of bound access when it is used functions like strlen(). The
  // buffer should only be used upto size MAX_HTTP_OUTPUT_BUFFER
  char local_response_buffer[MAX_HTTP_OUTPUT_BUFFER + 1] = {0};

  esp_http_client_config_t config = {
      .host = CONFIG_HTTP_ENDPOINT,
      .path = "/post",
      .query = "esp",
      .port = 6969,
      .event_handler = _http_event_handler,
      .user_data = local_response_buffer,
      .disable_auto_redirect = 1,
  };
  ESP_LOGI(HTTP_CLIENT_TAG, "HTTP request with url => %s/%s", config.host,
           config.path);
  esp_http_client_handle_t client = esp_http_client_init(&config);

  // Get
  // esp_err_t err = esp_http_client_perform(client);
  // if (err == ESP_OK) {
  //  ESP_LOGI(HTTP_CLIENT_TAG, "HTTP GET Status = %d, content_len = %" PRId64,
  //           esp_http_client_get_status_code(client),
  //           esp_http_client_get_content_length(client));
  //} else {
  //  ESP_LOGE(HTTP_CLIENT_TAG, "HTTP GET request fialed: %s",
  //           esp_err_to_name(err));
  //}
  // ESP_LOG_BUFFER_HEX(HTTP_CLIENT_TAG, local_response_buffer,
  //                   strlen(local_response_buffer));

  // POST
  const char *post_data =
      "{\"device_id\":\"test-esp32\",\"temp_c\":\"22\",\"humidity\":\"50\"}";
  // esp_http_client_set_url(client, "http://" CONFIG_HTTP_ENDPOINT "/post");
  esp_http_client_set_method(client, HTTP_METHOD_POST);
  esp_http_client_set_header(client, "Content-Type", "application/json");
  esp_http_client_set_post_field(client, post_data, strlen(post_data));
  esp_err_t err = esp_http_client_perform(client);
  if (err == ESP_OK) {
    ESP_LOGI(HTTP_CLIENT_TAG, "HTTP POST Status = %d, content_len = %" PRId64,
             esp_http_client_get_status_code(client),
             esp_http_client_get_content_length(client));
  } else {
    ESP_LOGE(HTTP_CLIENT_TAG, "HTTP POST request fialed: %s",
             esp_err_to_name(err));
  }

  esp_http_client_cleanup(client);
}

static void http_rest_with_hostname_path(void) {}

// DHT11
#define DHT11_GPIO CONFIG_DHT11_GPIO
// #define GPIO_INPUT_DHT11_PIN_SEL ((1ULL << DHT11_GPIO))

struct DHT11DATA {
  float humidity;
  float temp;
};

static float c_to_f(float tempc) {
  float temp_f = (tempc * 9.0f / 5.0f) + 32.0f;
  return temp_f;
}

void app_main(void) {
  // Initialize NVS
  esp_err_t ret = nvs_flash_init();
  if (ret == ESP_ERR_NVS_NO_FREE_PAGES ||
      ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
    ESP_ERROR_CHECK(nvs_flash_erase());
    ret = nvs_flash_init();
  }
  ESP_ERROR_CHECK(ret);

  if (CONFIG_LOG_MAXIMUM_LEVEL > CONFIG_LOG_DEFAULT_LEVEL) {
    esp_log_level_set("wifi", CONFIG_LOG_MAXIMUM_LEVEL);
  }

  ESP_LOGI(WIFI_TAG, "ESP_WIFI_MODE_STA");
  wifi_init_sta();

  http_rest_with_url();

  gpio_config_t io_conf = {};
  io_conf.intr_type = GPIO_INTR_DISABLE;
  io_conf.mode = GPIO_MODE_OUTPUT;
  io_conf.pin_bit_mask = GPIO_OUTPUT_LED_SEL;
  io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
  io_conf.pull_up_en = GPIO_PULLUP_DISABLE;
  gpio_config(&io_conf);

  struct DHT11DATA dht11_sensor;

  int cnt = 0;
  while (1) {
    esp_err_t err = dht_read_float_data(
        DHT_TYPE_DHT11, DHT11_GPIO, &dht11_sensor.humidity, &dht11_sensor.temp);
    if (err != 0) {
      ESP_LOGE(DHT11_TAG, "Could not read from DHT11");
    } else {
      ESP_LOGI(DHT11_TAG, "Humidity: %.2f, Temp: %.2f", dht11_sensor.humidity,
               c_to_f(dht11_sensor.temp));
    }
    if (cnt % 2 == 0) {
      ESP_LOGI(ESP32_GENERAL_TAG, "LED OFF");
    } else {
      ESP_LOGI(ESP32_GENERAL_TAG, "LED ON");
    }
    vTaskDelay(pdMS_TO_TICKS(3000));
    gpio_set_level(STATUS_LED_GPIO, cnt % 2);
    cnt++;
  }
}
