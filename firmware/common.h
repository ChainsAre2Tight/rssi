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

#define PERIODIC_SYNC_INTERVAL    64000UL  // ms -> 64s

#define UPLOAD_INTERVAL 10000 // 10 секунд

#define BASE_HOP_INTERVAL_MS 250
#define HOP_JITTER_MS        100

#define ANCHOR_CHANNEL       6

#define ANCHOR_PROBABILITY   50
#define STAY_PROBABILITY     20
#define BURST_PROBABILITY    15

#define BURST_MIN_HOPS       3
#define BURST_MAX_HOPS       6

// -------- SENSOR FOCUS CHANNEL 1 --------
// #define CHANNEL_PRESET_FOCUS_1

// -------- SENSOR FOCUS CHANNEL 6 --------
// #define CHANNEL_PRESET_FOCUS_6

// -------- SENSOR FOCUS CHANNEL 11 --------
// #define CHANNEL_PRESET_FOCUS_11

// -------- BALANCED SCANNING --------
// #define CHANNEL_PRESET_BALANCED


#if defined(CHANNEL_PRESET_FOCUS_1)

static const uint8_t CHANNEL_WEIGHT[13] = {
/*ch 1  2  3  4  5  6  7  8  9 10 11 12 13*/
   22,10, 6, 3, 3, 8, 3, 3, 3, 4, 8, 2, 2
};

#elif defined(CHANNEL_PRESET_FOCUS_6)

static const uint8_t CHANNEL_WEIGHT[13] = {
/*ch 1  2  3  4  5  6  7  8  9 10 11 12 13*/
    8, 4, 3, 3,10,24,10, 3, 3, 4, 8, 2, 2
};

#elif defined(CHANNEL_PRESET_FOCUS_11)

static const uint8_t CHANNEL_WEIGHT[13] = {
/*ch 1  2  3  4  5  6  7  8  9 10 11 12 13*/
    8, 4, 3, 3, 8, 8, 3, 3, 6,10,24, 6, 3
};

#elif defined(CHANNEL_PRESET_BALANCED)

static const uint8_t CHANNEL_WEIGHT[13] = {
/*ch 1  2  3  4  5  6  7  8  9 10 11 12 13*/
   14, 6, 4, 3, 6,14, 6, 3, 4, 6,14, 3, 3
};

#endif

uint8_t pickWeightedChannel() {
    static uint16_t total_weight = 0;
    static bool initialized = false;

    if (!initialized)
    {
        for (int i = 0; i < 13; i++)
        {
            total_weight += CHANNEL_WEIGHT[i];
        }
        initialized = true;
    }

    uint16_t r = esp_random() % total_weight;

    for (int i = 0; i < 13; i++)
    {
        if (r < CHANNEL_WEIGHT[i])
        {
            return i + 1;
        }

        r -= CHANNEL_WEIGHT[i];
    }

    return ANCHOR_CHANNEL;
}

void channelHoppingTask(void* pvParameter) {
    uint8_t current_channel = pickWeightedChannel();
    int burst_remaining = 0;

    while (true) {
        esp_wifi_set_channel(current_channel, WIFI_SECOND_CHAN_NONE);

        uint32_t r = esp_random() % 100;

        if (burst_remaining > 0) {
            // continue anchor burst
            current_channel = ANCHOR_CHANNEL;
            burst_remaining--;
        } else {
            if (r < BURST_PROBABILITY)
            {
                // start anchor burst
                burst_remaining =
                    BURST_MIN_HOPS +
                    (esp_random() % (BURST_MAX_HOPS - BURST_MIN_HOPS + 1));

                current_channel = ANCHOR_CHANNEL;
                burst_remaining--;
            } else if (r < BURST_PROBABILITY + STAY_PROBABILITY) {
                // stay on channel
            } else if (r < BURST_PROBABILITY + STAY_PROBABILITY + ANCHOR_PROBABILITY) {
                // jump to anchor
                current_channel = ANCHOR_CHANNEL;
            } else {
                // weighted random channel
                current_channel = pickWeightedChannel();
            }
        }

        int jitter = (esp_random() % (2 * HOP_JITTER_MS)) - HOP_JITTER_MS;
        int delay_ms = BASE_HOP_INTERVAL_MS + jitter;

        if (delay_ms < 10)
            delay_ms = 10;

        vTaskDelay(pdMS_TO_TICKS(delay_ms));
    }
}

void printTime() {
    struct tm timeinfo;
    getLocalTime(&timeinfo);
    Serial.println(&timeinfo, "%A, %B %d %Y %H:%M:%S");
}

void notify(struct timeval* t) {
    Serial.println("[TIME] SNPT sync recieved");
}

void wait4SNTP() {
    while (sntp_get_sync_status() != SNTP_SYNC_STATUS_COMPLETED) {
        delay(100);
        Serial.println("waiting ...");
    }
}

void syncSNTP() {
    Serial.printf("Before begin: %d\n", esp_timer_get_time());
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    Serial.printf("after begin: %d\n", esp_timer_get_time());
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
    sntp_set_sync_interval(60 * 1000UL);  // 1 minute
    sntp_set_time_sync_notification_cb(notify);
    esp_sntp_setoperatingmode(ESP_SNTP_OPMODE_POLL);
    esp_sntp_setservername(0, SNTP_SERVER);
    Serial.printf("Before sntp init: %d\n", esp_timer_get_time());
    esp_sntp_init();
    Serial.printf("after sntp init: %d\n", esp_timer_get_time());
    setenv("TZ", "MSK-3", 1);
    tzset();
    Serial.printf("Before sntp wait: %d\n", esp_timer_get_time());
    wait4SNTP();
    Serial.printf("after sntp wait: %d\n", esp_timer_get_time());
    Serial.printf("Before disconnect: %d\n", esp_timer_get_time());
    WiFi.disconnect(true);
    Serial.printf("after disconnect: %d\n", esp_timer_get_time());
}

#endif