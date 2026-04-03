#include <WiFi.h>
#include <HTTPClient.h>
#include "esp_sntp.h"
#include "esp_wifi.h"
#include "Arduino.h"

#include "../common.h"

#define DEVICE_NAME "ESP32_02"

struct CsiPacket {
    time_t time;
    uint8_t src_mac[6];
    uint8_t dst_mac[6];
    uint8_t bssid[6];
    int rssi;
    int channel;
    int type;
    int subtype;
    int seq;
};

CsiPacket buffer[MAX_PACKETS];
volatile int activeCount = 0;

void csiPacketHandler(void *ctx, wifi_csi_info_t *pkt) {
    if (activeCount >= MAX_PACKETS) return;

    CsiPacket p;
    memset(&p, 0, sizeof(CsiPacket));
    
    time(&p.time);

    wifi_pkt_rx_ctrl_t ctrl = pkt->rx_ctrl;
    uint8_t frame_ctrl1 = pkt->hdr[0];
    // uint8_t frame_ctrl2 = pkt->payload[1];
    p.type = (frame_ctrl1 >> 2) & 0x03;
    p.subtype = (frame_ctrl1 >> 4) & 0x0F;

    Serial.printf("t: %d, s: %d | %02X %02x %02X %02x %02X %02x %02X %02x \n", p.type, p.subtype, pkt->hdr[0], pkt->hdr[1], pkt->hdr[2], pkt->hdr[3], pkt->hdr[4], pkt->hdr[5], pkt->hdr[6], pkt->hdr[7]);

    if (p.type != 0 && p.type != 2) return;

    p.rssi = ctrl.rssi;
    p.channel = ctrl.channel;

    memcpy(p.src_mac, pkt->mac, 6);
    memcpy(p.dst_mac, pkt->dmac, 6);
    memcpy(p.bssid, pkt->hdr + 16, 6);

    p.seq = pkt->rx_seq;

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

    const int batchSize = 50;
    int sent = 0;

    while (sent < activeCount) {
        int end = sent + batchSize;
        if (end > activeCount) end = activeCount;
        Serial.printf("sent: %d, batchsize: %d, end: %d, activecount: %d\n", sent, batchSize, end, activeCount);

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
            json += "\"time\":" + String(buffer[i].time) + ",";
            json += "\"rssi\":" + String(buffer[i].rssi) + ",";
            json += "\"ch\":" + String(buffer[i].channel) + ",";
            json += "\"type\":" + String(buffer[i].type) + ",";
            json += "\"sub\":" + String(buffer[i].subtype) + ",";
            json += "\"seq\":" + String(buffer[i].seq) + ",";
            json += "\"src\":\"" + String(mac1) + "\",";
            json += "\"dst\":\"" + String(mac2) + "\",";
            json += "\"bssid\":\"" + String(mac3) + "\"";
            json += "}";
            if (i != end - 1) json += ",";
        }
        json += "]}";

        HTTPClient http;
        http.begin(SERVER_URL_CSI);
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

    // syncSNTP();
    initSniffer();
    // xTaskCreatePinnedToCore(channelHoppingTask, "ChannelHopping", 2048, NULL, 1, NULL, 1);
    digitalWrite(LED_BUILTIN, HIGH);

}

unsigned long lastUpload = 0;


void loop() {
    unsigned long now = millis();
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
