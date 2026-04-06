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
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER NOT NULL,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT,
                FOREIGN KEY (room_id) REFERENCES rooms(id)
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
                FOREIGN KEY (measurement_id) REFERENCES measurements(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS packets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                measurement_id INTEGER,
                device TEXT,
                boot_time_us INTEGER,
                unix_time_us INTEGER,
                rssi INTEGER,
                noise_floor INTEGER,
                channel INTEGER,
                type INTEGER,
                subtype INTEGER,
                seq INTEGER,
                src_mac TEXT,
                dst_mac TEXT,
                bssid TEXT,
                ssid TEXT,
                processed INTEGER DEFAULT 0,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device) REFERENCES devices(name),
                FOREIGN KEY (measurement_id) REFERENCES measurements(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS csi_packets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                measurement_id INTEGER,
                device TEXT,
                boot_time_us INTEGER,
                unix_time_us INTEGER,
                rssi INTEGER,
                noise_floor INTEGER,
                channel INTEGER,
                type INTEGER,
                subtype INTEGER,
                seq INTEGER,
                src_mac TEXT,
                dst_mac TEXT,
                bssid TEXT,
                csi TEXT,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device) REFERENCES devices(name),
                FOREIGN KEY (measurement_id) REFERENCES measurements(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                measurement_id INTEGER NOT NULL,
                src_mac TEXT NOT NULL,
                seq INTEGER NOT NULL,
                type INTEGER NOT NULL,
                subtype INTEGER NOT NULL,
                dst_mac TEXT,
                bssid TEXT,
                ssid TEXT,
                first_time_us INTEGER NOT NULL,
                last_time_us INTEGER NOT NULL,
                approx_unix_time_us INTEGER NOT NULL,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (measurement_id) REFERENCES measurements(id)
            )
        """)

        # could as well be one-to-many table...
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                device TEXT NOT NULL,
                boot_time_us INTEGER NOT NULL,
                unix_time_us INTEGER NOT NULL,
                rssi INTEGER,
                noise_floor INTEGER,
                channel INTEGER,
                packet_id INTEGER,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
                FOREIGN KEY (device) REFERENCES devices(name),
                FOREIGN KEY (packet_id) REFERENCES packets(id)
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_packets_measurement_time
            ON packets(measurement_id, boot_time_us)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_measurement_time
            ON events(measurement_id, approx_unix_time_us)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_src_time
            ON events(src_mac, approx_unix_time_us)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_event_obs_event
            ON event_observations(event_id)
        """)

        conn.commit()


if __name__ == "__main__":
    init_db()