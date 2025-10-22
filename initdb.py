import storage


def init_db():
    with storage.Connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS packets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device TEXT,
                tsf TEXT,
                rssi INTEGER,
                channel INTEGER,
                type INTEGER,
                subtype INTEGER,
                seq INTEGER,
                src_mac TEXT,
                dst_mac TEXT,
                bssid TEXT,
                ssid TEXT
            )
        """)
        conn.commit()

if __name__ == "__main__":
    init_db()