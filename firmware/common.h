#ifndef _COMMON_
#define _COMMON_ 1

#include <stdint.h>
#include <string.h>

#include <WiFi.h>
#include <HTTPClient.h>
#include "Arduino.h"
#include "esp_sntp.h"
#include "esp_wifi.h"
#include "esp_system.h"

// ==== Настройки Wi-Fi и сервера ====
#define WIFI_SSID "dmitry-moosetop"
#define WIFI_PASS "gQmB9LdM"
#define SNTP_SERVER "10.42.0.1"
#define SERVER_URL "http://10.42.0.1:5000"

#define API_URL_REGULAR SERVER_URL "/upload"
#define API_URL_CSI SERVER_URL "/upload-csi"
#define API_URL_SNTP_UPDATE SERVER_URL "/sync"

// #define WIFI_SSID "WIN-RPM7N83F4EC 3999"
// #define WIFI_PASS "3vA=8168"
// #define SNTP_SERVER "192.168.137.1"
// #define SERVER_URL "http://192.168.137.1/upload"

// ==== Настройки сниффера ====
#define MAX_PACKETS 500
#define CYCLES_BEFORE_RESYNC 10
static int cycle_counter = 0;

#define UPLOAD_INTERVAL 10000 // 10 секунд

#define BASE_HOP_INTERVAL_MS 250
#define HOP_JITTER_MS        100

static const uint8_t SCAN_CHANNELS[] = {1, 6, 11};
static const size_t NUM_SCAN_CHANNELS = sizeof(SCAN_CHANNELS) / sizeof(SCAN_CHANNELS[0]);

void channelHoppingTask(void* pvParameter)
{
    size_t index = 0;

    while (true) {

        uint8_t channel = SCAN_CHANNELS[index];
        esp_wifi_set_channel(channel, WIFI_SECOND_CHAN_NONE);

        // Move to next channel
        index = (index + 1) % NUM_SCAN_CHANNELS;

        // Random jitter: [-JITTER, +JITTER]
        int jitter = (esp_random() % (2 * HOP_JITTER_MS)) - HOP_JITTER_MS;
        int delay_ms = BASE_HOP_INTERVAL_MS + jitter;

        if (delay_ms < 10) {
            delay_ms = 10; // safety minimum
        }

        vTaskDelay(pdMS_TO_TICKS(delay_ms));
    }
}

void printTime() {
    struct tm timeinfo;
    getLocalTime(&timeinfo);
    Serial.println(&timeinfo, "%A, %B %d %Y %H:%M:%S");
}

static __INT64_TYPE__ boot_time_us = 0;
static time_t boot_unix_time = 0;
static bool server_sntp_resync_pending = false;

void notify(struct timeval* t) {
    boot_time_us = esp_timer_get_time();
    time(&boot_unix_time);
    server_sntp_resync_pending = true;
    Serial.println("time synchronized");
    printTime();
}

void send_sntp_resync(String device_name) {
    Serial.println("[HTTP] Sending SNTP sync data");
    String json = "{\"device\":\"" + device_name
    + "\", \"boot_time_us\":" + String(boot_time_us)
    + ", \"boot_unix_time\":" + String(boot_unix_time) + "}";

    HTTPClient http;
    http.begin(API_URL_SNTP_UPDATE);
    http.addHeader("Content-Type", "application/json");
    int httpCode = http.POST(json);
    if (httpCode == 200) {
        Serial.printf("[HTTP] Success! Response: %d\n", httpCode);
        server_sntp_resync_pending = false;
    } else if (httpCode > 0) {
        Serial.printf("[HTTP] Error! Response: %d\n", httpCode);
    } else {
        Serial.printf("[HTTP] Error: %s\n", http.errorToString(httpCode).c_str());
    }
    http.end();
}

void wait4SNTP() {
    while (sntp_get_sync_status() != SNTP_SYNC_STATUS_COMPLETED) {
        delay(100);
        Serial.println("waiting ...");
    }
}

void syncSNTP() {
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    Serial.print("[WIFI] Connecting for SNTP sync...");
    int retry = 0;
    digitalWrite(LED_BUILTIN, LOW);
    while (WiFi.status() != WL_CONNECTED) {
        digitalWrite(LED_BUILTIN, LOW);
        delay(300);
        digitalWrite(LED_BUILTIN, HIGH);
        delay(200);
        Serial.print(".");
        retry++;
    }
    digitalWrite(LED_BUILTIN, LOW);
    Serial.println();

    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("[WIFI] Failed to connect");
        return;
    }
    delay(50);
    digitalWrite(LED_BUILTIN, HIGH);
    delay(50);
    digitalWrite(LED_BUILTIN, LOW);
    Serial.println("[WIFI] Connected, syncing time...");
    sntp_set_sync_interval(1 * 60 * 60 * 1000UL);  // 1 hour
    sntp_set_time_sync_notification_cb(notify);
    esp_sntp_setoperatingmode(ESP_SNTP_OPMODE_POLL);
    esp_sntp_setservername(0, SNTP_SERVER);
    esp_sntp_init();
    setenv("TZ", "MSK-3", 1);
    tzset();
    wait4SNTP();
}

#endif