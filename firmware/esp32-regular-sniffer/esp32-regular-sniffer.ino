#include <WiFi.h>
#include <HTTPClient.h>
#include "esp_sntp.h"
#include "esp_wifi.h"
#include "Arduino.h"

#define CHANNEL_PRESET_FOCUS_1
#define DEVICE_NAME "ESP32_01"

// #define CHANNEL_PRESET_FOCUS_6
// #define DEVICE_NAME "ESP32_03"

// #define CHANNEL_PRESET_FOCUS_11
// #define DEVICE_NAME "ESP32_07"

#include "../common.h"

#define MAX_PACKETS 512

struct Packet {
    int64_t boot_time_us;
    int64_t unix_time_us;
    uint8_t src_mac[6];
    uint8_t dst_mac[6];
    uint8_t bssid[6];
    int rssi;
    int noise_floor;
    int channel;
    int type;
    int subtype;
    int seq;
    char ssid[33];
};

Packet buffer[MAX_PACKETS];
volatile int activeCount = 0;

String jsonEscape(const char* str) {
    String s = "";
    while (*str) {
        if (*str == '\"') s += "\\\"";
        else if (*str == '\\') s += "\\\\";
        else if (*str >= 0 && *str <= 0x1F) s += ' ';
        else s += *str;
        str++;
    }
    return s;
}

void packetHandler(void* buf, wifi_promiscuous_pkt_type_t type) {
    if (activeCount >= MAX_PACKETS) return;
    int64_t capture_time = esp_timer_get_time();

    struct timeval tv;
    gettimeofday(&tv, NULL);

    wifi_promiscuous_pkt_t* pkt = (wifi_promiscuous_pkt_t*)buf;

    Packet p;
    memset(&p, 0, sizeof(Packet));
    p.boot_time_us = capture_time;
    p.unix_time_us = (int64_t)tv.tv_sec * 1000000LL + tv.tv_usec;

    wifi_pkt_rx_ctrl_t ctrl = pkt->rx_ctrl;
    p.rssi = ctrl.rssi;
    p.noise_floor = ctrl.noise_floor;
    p.channel = ctrl.channel;

    memcpy(p.src_mac, pkt->payload + 10, 6);
    memcpy(p.dst_mac, pkt->payload + 4, 6);
    memcpy(p.bssid, pkt->payload + 16, 6);

    uint8_t frame_ctrl1 = pkt->payload[0];
    p.type = (frame_ctrl1 >> 2) & 0x03;
    p.subtype = (frame_ctrl1 >> 4) & 0x0F;

    if (p.type != 0 && p.type != 2) return;

    p.seq = (((pkt->payload[22] << 8) | pkt->payload[23])) >> 4;

    if (p.type == 0 && (
        p.subtype == 0 || p.subtype == 2 || p.subtype == 4 || p.subtype == 5 || p.subtype == 8
        )
    ) { 
        int ssid_start = -1;  // default: not present / unknown

        switch (p.subtype) {
            case 0: // Association Request
                ssid_start = 28; // 24 + 4
                break;

            case 2: // Reassociation Request
                ssid_start = 34; // 24 + 10
                break;

            case 4: // Probe Request
                ssid_start = 24; // 24 + 0
                break;

            case 5: // Probe Response
                ssid_start = 36; // 24 + 12
                break;

            case 8: // Beacon
                ssid_start = 36; // 24 + 12
                break;

            default:
                ssid_start = -1; // no SSID in this subtype
                break;
        }

        uint8_t ssid_len = pkt->payload[ssid_start+1];
        if (ssid_len > 32) ssid_len = 32;

        for (int i = 0; i < ssid_len; i++) {
            char c = pkt->payload[ssid_start + i + 2];
            if (c >= 32 && c <= 126)  // только печатаемые ASCII
                p.ssid[i] = c;
            else
                p.ssid[i] = '?';  // заменяем "плохие" символы
        }
        p.ssid[ssid_len] = '\0';
    }

    buffer[activeCount++] = p;
}

void initSniffer() {
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));
    ESP_ERROR_CHECK(esp_wifi_set_storage(WIFI_STORAGE_RAM));
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_NULL));
    ESP_ERROR_CHECK(esp_wifi_start());

    ESP_ERROR_CHECK(esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE));

    wifi_promiscuous_filter_t filter = {};
    filter.filter_mask = WIFI_PROMIS_FILTER_MASK_MGMT | WIFI_PROMIS_FILTER_MASK_DATA;
    ESP_ERROR_CHECK(esp_wifi_set_promiscuous_filter(&filter));
    ESP_ERROR_CHECK(esp_wifi_set_promiscuous_rx_cb(&packetHandler));
    ESP_ERROR_CHECK(esp_wifi_set_promiscuous(true));

    Serial.println("[SNIFFER] Promiscuous ENABLED");

    
}

void sendBatch() {
    if (activeCount == 0) {
        Serial.println("[UPLOAD] No packets to send");
        return;
    }

    WiFi.begin(WIFI_SSID, WIFI_PASS);
    Serial.print("[WIFI] Connecting");
    int retry = 0;
    digitalWrite(LED_BUILTIN, LOW);
    while (WiFi.status() != WL_CONNECTED && retry < 20) {
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
    delay(50);
    digitalWrite(LED_BUILTIN, HIGH);
    delay(50);
    digitalWrite(LED_BUILTIN, LOW);
    delay(50);
    digitalWrite(LED_BUILTIN, HIGH);
    delay(50);
    digitalWrite(LED_BUILTIN, LOW);
    Serial.println("[WIFI] Connected, sending batch...");

    int sync_attempts = 0;
    while (server_sntp_resync_pending && sync_attempts < 3) {
        send_sntp_resync(String(DEVICE_NAME));
        sync_attempts++;
        delay(50);
    }

    const int batchSize = 64;
    int sent = 0;

    while (sent < activeCount) {
        int end = sent + batchSize;
        if (end > activeCount) end = activeCount;

        String json = "{\"device\":\"" + String(DEVICE_NAME) + "\",\"batch_ts\":\"" + String(millis()) + "\",\"packets\":[";
        for (int i = sent; i < end; i++) {
            char mac1[18], mac2[18], mac3[18];
            snprintf(mac1, sizeof(mac1), "%02X:%02X:%02X:%02X:%02X:%02X",
                     buffer[i].src_mac[0], buffer[i].src_mac[1], buffer[i].src_mac[2],
                     buffer[i].src_mac[3], buffer[i].src_mac[4], buffer[i].src_mac[5]);
            snprintf(mac2, sizeof(mac2), "%02X:%02X:%02X:%02X:%02X:%02X",
                     buffer[i].dst_mac[0], buffer[i].dst_mac[1], buffer[i].dst_mac[2],
                     buffer[i].dst_mac[3], buffer[i].dst_mac[4], buffer[i].dst_mac[5]);
            snprintf(mac3, sizeof(mac3), "%02X:%02X:%02X:%02X:%02X:%02X",
                     buffer[i].bssid[0], buffer[i].bssid[1], buffer[i].bssid[2],
                     buffer[i].bssid[3], buffer[i].bssid[4], buffer[i].bssid[5]);

            String ssidSafe = buffer[i].ssid[0] ? jsonEscape(buffer[i].ssid) : "";

            json += "{";
            json += "\"boot_time_us\":" + String(buffer[i].boot_time_us) + ",";
            json += "\"unix_time_us\":" + String(buffer[i].unix_time_us) + ",";
            json += "\"rssi\":" + String(buffer[i].rssi) + ",";
            json += "\"noise_floor\":" + String(buffer[i].noise_floor) + ",";
            json += "\"ch\":" + String(buffer[i].channel) + ",";
            json += "\"type\":" + String(buffer[i].type) + ",";
            json += "\"sub\":" + String(buffer[i].subtype) + ",";
            json += "\"seq\":" + String(buffer[i].seq) + ",";
            json += "\"src\":\"" + String(mac1) + "\",";
            json += "\"dst\":\"" + String(mac2) + "\",";
            json += "\"bssid\":\"" + String(mac3) + "\",";
            json += "\"ssid\":\"" + ssidSafe + "\"";
            json += "}";
            if (i != end - 1) json += ",";
        }
        json += "]}";

        HTTPClient http;
        http.begin(API_URL_REGULAR);
        http.addHeader("Content-Type", "application/json");
        int httpCode = http.POST(json);
        if (httpCode > 0) {
            Serial.printf("[HTTP] Response: %d\n", httpCode);
        } else {
            Serial.printf("[HTTP] Error: %s\n", http.errorToString(httpCode).c_str());
        }
        http.end();

        sent = end;
    }

    activeCount = 0;
    WiFi.disconnect(true);
    Serial.printf("[UPLOAD] Sent total %d records\n", sent);
}

void setup() {
    pinMode(LED_BUILTIN, OUTPUT);
    Serial.begin(115200);
    digitalWrite(LED_BUILTIN, HIGH);
    syncSNTP();
    initSniffer();
    xTaskCreatePinnedToCore(channelHoppingTask, "ChannelHopping", 2048, NULL, 1, NULL, 1);
}

unsigned long lastUpload = 0;

void loop() {
    unsigned long now = millis();

#if PERIODIC_TIME_SYNC
    if (now - lastPeriodicSync > PERIODIC_SYNC_INTERVAL) {
        generatePeriodicSync();
        lastPeriodicSync = now;
    }
#endif

    if (now - lastUpload > UPLOAD_INTERVAL) {
        Serial.println("[SNIFFER] Promiscuous DISABLED");
        digitalWrite(LED_BUILTIN, LOW);
        esp_wifi_set_promiscuous(false);
        delay(50);

        sendBatch();

        initSniffer();

        lastUpload = now;
        digitalWrite(LED_BUILTIN, HIGH);
    }

    delay(500);
}
