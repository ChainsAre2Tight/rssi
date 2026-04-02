#include <WiFi.h>
#include <HTTPClient.h>
#include "esp_sntp.h"
#include "esp_wifi.h"
#include "Arduino.h"

// ==== Настройки Wi-Fi и сервера ====
#define WIFI_SSID "dmitry-moosetop"
#define WIFI_PASS "gQmB9LdM"
#define SNTP_SERVER "10.42.0.1"
#define SERVER_URL "http://10.42.0.1:5000/upload"

// #define WIFI_SSID "WIN-RPM7N83F4EC 3999"
// #define WIFI_PASS "3vA=8168"
// #define SNTP_SERVER "192.168.137.1"
// #define SERVER_URL "http://192.168.137.1/upload"

#define DEVICE_NAME "ESP32_09"

// ==== Настройки сниффера ====
#define MAX_PACKETS 500
#define HOP_INTERVAL_MS 500
#define NUM_CHANNELS 13

struct Packet {
    time_t time;
    uint8_t src_mac[6];
    uint8_t dst_mac[6];
    uint8_t bssid[6];
    int rssi;
    int channel;
    int type;
    int subtype;
    int seq;
    char ssid[33];
    uint64_t tsf;
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

void packetHandler(void *ctx, wifi_csi_info_t *pkt) {
    if (activeCount >= MAX_PACKETS) return;
    // if (pkt->payload[]-> != WIFI_PKT_MGMT) return;

    

    Packet p;
    memset(&p, 0, sizeof(Packet));
    
    time(&p.time);

    wifi_pkt_rx_ctrl_t ctrl = pkt->rx_ctrl;
    uint8_t frame_ctrl1 = pkt->hdr[0];
    // uint8_t frame_ctrl2 = pkt->payload[1];
    p.type = (frame_ctrl1 >> 2) & 0x03;
    p.subtype = (frame_ctrl1 >> 4) & 0x0F;

    Serial.printf("t: %d, s: %d | %02X %02x %02X %02x %02X %02x %02X %02x \n", p.type, p.subtype, pkt->hdr[0], pkt->hdr[1], pkt->hdr[2], pkt->hdr[3], pkt->hdr[4], pkt->hdr[5], pkt->hdr[6], pkt->hdr[7]);

    if (p.type != 0) return;

    p.rssi = ctrl.rssi;
    p.channel = ctrl.channel;
    p.tsf = esp_timer_get_time();

    memcpy(p.src_mac, pkt->mac, 6);
    memcpy(p.dst_mac, pkt->dmac, 6);
    memcpy(p.bssid, pkt->hdr + 16, 6);

    p.seq = pkt->rx_seq;
    

    int ssid_begin = 0;
    if (p.subtype == 4) {
        ssid_begin = 13;
    } else if (p.subtype == 4 || p.subtype == 5 || p.subtype == 8) {
        ssid_begin = 24;
    }

    uint8_t ssid_len = pkt->payload[ssid_begin];
    if (ssid_len > 32) ssid_len = 32;

    for (int i = 0; i < 32; i++) {
        char c = pkt->payload[ssid_begin + i + 1];
        if (c >= 32 && c <= 126)  // только печатаемые ASCII
            p.ssid[i] = c;
        else
            p.ssid[i] = '?';  // заменяем "плохие" символы
    }
    p.ssid[32] = '\0';

    buffer[activeCount++] = p;
}

void channelHoppingTask(void* pvParameter) {
    uint8_t channel = 1;
    while (true) {
        esp_wifi_set_channel(channel, WIFI_SECOND_CHAN_NONE);
        channel = (channel % NUM_CHANNELS) + 1;
        vTaskDelay(HOP_INTERVAL_MS / portTICK_PERIOD_MS);
    }
}

void initSniffer() {
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));
    ESP_ERROR_CHECK(esp_wifi_set_storage(WIFI_STORAGE_RAM));
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_NULL));
    ESP_ERROR_CHECK(esp_wifi_start());
    ESP_ERROR_CHECK(esp_wifi_set_channel(6, WIFI_SECOND_CHAN_NONE));

    wifi_promiscuous_filter_t filter = {};
    // filter.filter_mask = WIFI_PROMIS_FILTER_MASK_MGMT;
    // ESP_ERROR_CHECK(esp_wifi_set_promiscuous_filter(&filter));
    // ESP_ERROR_CHECK(esp_wifi_set_promiscuous_rx_cb(&packetHandler));
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
    ESP_ERROR_CHECK(esp_wifi_set_csi_rx_cb(packetHandler, NULL));
    ESP_ERROR_CHECK(esp_wifi_set_csi(true));

    Serial.println("[SNIFFER] Promiscuous ENABLED");
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

void printTime() {
    struct tm timeinfo;
    getLocalTime(&timeinfo);
    Serial.println(&timeinfo, "%A, %B %d %Y %H:%M:%S");
}

void notify(struct timeval* t) {
    Serial.println("time synchronized");
    printTime();
}

void wait4SNTP() {
    while (sntp_get_sync_status() != SNTP_SYNC_STATUS_COMPLETED) {
        delay(100);
        Serial.println("waiting ...");
    }
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
            json += "\"time\":" + String(buffer[i].time) + ",";
            json += "\"ts\":" + String(buffer[i].tsf) + ",";
            json += "\"rssi\":" + String(buffer[i].rssi) + ",";
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
        http.begin(SERVER_URL);
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
const unsigned long UPLOAD_INTERVAL = 10000; // 10 секунд

void loop() {
    unsigned long now = millis();
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
