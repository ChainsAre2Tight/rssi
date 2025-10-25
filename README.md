## MAC esp32:
- **ESP32_01** ```00:4B:12:2F:C0:44```
- **ESP32_02** ```00:4B:12:2F:7C:B0```
- **ESP32_03** ```-```
- **ESP32_04** ```-```
- **ESP32_05** ```-```

## Cхема данных

```
PACKETS:
id              device      tsf     rssi    channel type    subtype seq     src_mac dst_mac bssid   ssid
INTEGER         TEXT        TEXT    INTEGER INTEGER INTEGER INTEGER INTEGER TEXT    TEXT    TEXT    TEXT
PRIMARY KEY     NOT NULL    
AUTOINCREMENT
```

## Пример .env
```env
DB_PATH="database.db"
NAME="skibidi"

ROOM_ID=1
MEASUREMENT_ID=8

VIZ_ROOM_ID=1
VIZ_MEASUREMENT_ID=8
VIZ_SSID="dmitry-moosetop"
# VIZ_SSID="Leather club"
# VIZ_SSID="Leather Club Mini"

PATH_LOSS_EXPONENT=3
ESP32_SIGNAL_STRENGTH=-80.0
```