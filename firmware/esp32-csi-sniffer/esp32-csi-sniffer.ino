#include <WiFi.h>
#include <HTTPClient.h>
#include "esp_sntp.h"
#include "esp_wifi.h"
#include "Arduino.h"
#include <stdlib.h>

#define CHANNEL_PRESET_BALANCED

#define DEVICE_NAME "ESP32_02"
// #define DEVICE_NAME "ESP32_04"
// #define DEVICE_NAME "ESP32_08"

#include "../common.h"

struct CsiPacket {
    int64_t boot_time_us;
    uint8_t src_mac[6];
    uint8_t dst_mac[6];
    uint8_t bssid[6];
    int rssi;
    int noise_floor;
    int channel;
    int type;
    int subtype;
    int seq;
    uint16_t csi_length;
    int8_t* csi_buffer;
};

CsiPacket buffer[MAX_PACKETS];
volatile int activeCount = 0;

unsigned long lastUpload = 0;

void csiPacketHandler(void *ctx, wifi_csi_info_t *pkt) {

    int64_t capture_time = esp_timer_get_time();
    if (activeCount >= MAX_PACKETS) return;

    CsiPacket p;
    memset(&p, 0, sizeof(CsiPacket));

    p.boot_time_us = capture_time;

    wifi_pkt_rx_ctrl_t rx_ctrl = pkt->rx_ctrl;

    uint8_t frame_ctrl1 = pkt->hdr[0];
    p.type = (frame_ctrl1 >> 2) & 0x03;
    p.subtype = (frame_ctrl1 >> 4) & 0x0F;

    if (p.type != 0 && p.type != 2) return;

    p.rssi = rx_ctrl.rssi;
    p.channel = rx_ctrl.channel;

    memcpy(p.src_mac, pkt->mac, 6);
    memcpy(p.dst_mac, pkt->dmac, 6);
    memcpy(p.bssid, pkt->hdr + 16, 6);

    p.seq = pkt->rx_seq;
    p.noise_floor = rx_ctrl.noise_floor;
    p.csi_length = pkt->len;

    p.csi_buffer = (int8_t*)malloc(p.csi_length * sizeof(int8_t));
    memcpy(p.csi_buffer, pkt->buf, p.csi_length * sizeof(int8_t));

    buffer[activeCount++] = p;
}

void initSniffer() {

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();

    ESP_ERROR_CHECK(esp_wifi_init(&cfg));
    ESP_ERROR_CHECK(esp_wifi_set_storage(WIFI_STORAGE_RAM));
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_NULL));
    ESP_ERROR_CHECK(esp_wifi_start());

    ESP_ERROR_CHECK(esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE));
    ESP_ERROR_CHECK(esp_wifi_set_promiscuous(true));

    wifi_csi_config_t csi_config = {
        .lltf_en           = true,
        .htltf_en          = true,
        .stbc_htltf2_en    = true,
        .ltf_merge_en      = true,
        .channel_filter_en = true,
        .manu_scale        = false,
        .shift             = false,
        .dump_ack_en       = true,
    };

    ESP_ERROR_CHECK(esp_wifi_set_csi_config(&csi_config));
    ESP_ERROR_CHECK(esp_wifi_set_csi_rx_cb(csiPacketHandler, NULL));
    ESP_ERROR_CHECK(esp_wifi_set_csi(true));

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

    digitalWrite(LED_BUILTIN, HIGH); delay(50);
    digitalWrite(LED_BUILTIN, LOW);  delay(50);
    digitalWrite(LED_BUILTIN, HIGH); delay(50);
    digitalWrite(LED_BUILTIN, LOW);  delay(50);
    digitalWrite(LED_BUILTIN, HIGH); delay(50);
    digitalWrite(LED_BUILTIN, LOW);

    Serial.println("[WIFI] Connected, sending batch...");

    int sync_attempts = 0;

    while (server_sntp_resync_pending && sync_attempts < 3) {

        send_sntp_resync(String(DEVICE_NAME));

        sync_attempts++;
        delay(50);
    }

    const int batchSize = 50;

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

            json += "{";
            json += "\"boot_time_us\":" + String(buffer[i].boot_time_us) + ",";
            json += "\"rssi\":" + String(buffer[i].rssi) + ",";
            json += "\"noise_floor\":" + String(buffer[i].noise_floor) + ",";
            json += "\"ch\":" + String(buffer[i].channel) + ",";
            json += "\"type\":" + String(buffer[i].type) + ",";
            json += "\"sub\":" + String(buffer[i].subtype) + ",";
            json += "\"seq\":" + String(buffer[i].seq) + ",";
            json += "\"src\":\"" + String(mac1) + "\",";
            json += "\"dst\":\"" + String(mac2) + "\",";
            json += "\"bssid\":\"" + String(mac3) + "\",";
            json += "\"csi\":[";

            for (int j = 0; j < buffer[i].csi_length; j++) {
                json += String(buffer[i].csi_buffer[j]);
                if (j != buffer[i].csi_length - 1) json += ",";
            }

            json += "]";
            json += "}";

            if (i != end - 1) json += ",";

            free(buffer[i].csi_buffer);
        }

        json += "]}";

        HTTPClient http;

        http.begin(API_URL_CSI);
        http.addHeader("Content-Type", "application/json");

        int httpCode = http.POST(json);

        if (httpCode > 0)
            Serial.printf("[HTTP] Response: %d\n", httpCode);
        else
            Serial.printf("[HTTP] Error: %s\n", http.errorToString(httpCode).c_str());

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

    syncSNTP();

    initSniffer();

    xTaskCreatePinnedToCore(channelHoppingTask, "ChannelHopping", 2048, NULL, 1, NULL, 1);

    digitalWrite(LED_BUILTIN, HIGH);
}

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

        ESP_ERROR_CHECK(esp_wifi_set_csi_rx_cb(NULL, NULL));

        delay(50);

        sendBatch();

        initSniffer();

        lastUpload = now;

        digitalWrite(LED_BUILTIN, HIGH);
    }

    delay(500);
}