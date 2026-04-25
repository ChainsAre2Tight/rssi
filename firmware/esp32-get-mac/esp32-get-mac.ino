#include "WiFi.h"

void setup() {
  Serial.begin(115200);
  Serial.println("Network address:");
  Serial.println(Network.macAddress());
  Serial.println("WiFi STA address:");
  WiFi.STA.begin();
  Serial.println(WiFi.STA.macAddress());
}

void loop() {
  
}