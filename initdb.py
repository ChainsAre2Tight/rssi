import storage


def init_db():
    with storage.Connect() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                name TEXT PRIMARY KEY,
                description TEXT,
                mac TEXT UNIQUE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER NOT NULL,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT,
                FOREIGN KEY (room_id) REFERENCES room(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                measurement_id INTEGER NOT NULL,
                device TEXT NOT NULL,
                description TEXT,
                x REAL NOT NULL,
                y REAL NOT NULL,
                z REAL NOT NULL,
                PRIMARY KEY (measurement_id, device),
                FOREIGN KEY (device) REFERENCES devices(name),
                FOREIGN KEY (measurement_id) REFERENCES measurement(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT,
                x REAL NOT NULL,
                y REAL NOT NULL,
                z REAL NOT NULL,
                coeff REAL NOT NULL DEFAULT 2.0
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS packets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                measurement_id INTEGER,
                device TEXT,
                time INTEGER,
                rssi INTEGER,
                channel INTEGER,
                type INTEGER,
                subtype INTEGER,
                seq INTEGER,
                src_mac TEXT,
                dst_mac TEXT,
                bssid TEXT,
                ssid TEXT,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device) REFERENCES devices(name),
                FOREIGN KEY (measurement_id) REFERENCES measurement(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS csi_packets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                measurement_id INTEGER,
                device TEXT,
                time INTEGER,
                rssi INTEGER,
                channel INTEGER,
                type INTEGER,
                subtype INTEGER,
                seq INTEGER,
                src_mac TEXT,
                dst_mac TEXT,
                bssid TEXT,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device) REFERENCES devices(name),
                FOREIGN KEY (measurement_id) REFERENCES measurement(id)
            )
        """)
        conn.commit()

if __name__ == "__main__":
    init_db()