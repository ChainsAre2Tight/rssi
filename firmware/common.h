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
#define CYCLES_BEFORE_RESYNC 3
static int cycle_counter = 0;

#define UPLOAD_INTERVAL 10000 // 10 секунд

#define BASE_HOP_INTERVAL_MS 250
#define HOP_JITTER_MS        100

#define ANCHOR_CHANNEL       6

#define ANCHOR_PROBABILITY   50   // % chance to go to anchor
#define STAY_PROBABILITY     20   // % chance to stay on current channel
#define BURST_PROBABILITY    15   // % chance to start anchor burst

#define BURST_MIN_HOPS       3
#define BURST_MAX_HOPS       6

static const uint8_t CHANNELS[] = {1, 6, 11};
static const size_t NUM_CHANNELS = sizeof(CHANNELS) / sizeof(CHANNELS[0]);

void channelHoppingTask(void* pvParameter)
{
    uint8_t current_channel = CHANNELS[esp_random() % NUM_CHANNELS];

    int burst_remaining = 0;

    while (true)
    {
        esp_wifi_set_channel(current_channel, WIFI_SECOND_CHAN_NONE);

        uint32_t r = esp_random() % 100;

        if (burst_remaining > 0)
        {
            // Continue anchor burst
            current_channel = ANCHOR_CHANNEL;
            burst_remaining--;
        }
        else
        {
            if (r < BURST_PROBABILITY)
            {
                // Start anchor burst
                burst_remaining =
                    BURST_MIN_HOPS +
                    (esp_random() % (BURST_MAX_HOPS - BURST_MIN_HOPS + 1));

                current_channel = ANCHOR_CHANNEL;
                burst_remaining--;
            }
            else if (r < BURST_PROBABILITY + STAY_PROBABILITY)
            {
                // Stay on same channel
            }
            else if (r < BURST_PROBABILITY + STAY_PROBABILITY + ANCHOR_PROBABILITY)
            {
                // Move to anchor
                current_channel = ANCHOR_CHANNEL;
            }
            else
            {
                // Random channel
                current_channel = CHANNELS[esp_random() % NUM_CHANNELS];
            }
        }

        int jitter = (esp_random() % (2 * HOP_JITTER_MS)) - HOP_JITTER_MS;
        int delay_ms = BASE_HOP_INTERVAL_MS + jitter;

        if (delay_ms < 10) delay_ms = 10;

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
    boot_unix_time = (int64_t)t->tv_sec * 1000000LL + t->tv_usec;

    server_sntp_resync_pending = true;
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