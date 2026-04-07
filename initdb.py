import storage


def init_db():
    with storage.Session() as conn:

        # enforce it here if disabled for debug in regular config
        conn.execute("PRAGMA foreign_keys = ON")

        with storage.Transaction(conn) as t:
            cursor = t.cursor()

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
                CREATE TABLE IF NOT EXISTS windows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    measurement_id INTEGER NOT NULL,
                    layer INTEGER NOT NULL,
                    sequence_id INTEGER NOT NULL,
                    start_time_us INTEGER NOT NULL,
                    end_time_us INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    processing_started_at INTEGER,
                    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(measurement_id, layer, sequence_id),
                    FOREIGN KEY (measurement_id) REFERENCES measurements(id)
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_windows_measurement_status_time
                ON windows(measurement_id, status, end_time_us)
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    measurement_id INTEGER NOT NULL,
                    window_id INTEGER NOT NULL,
                    observation_id INTEGER,
                    role TEXT,
                    src_mac TEXT NOT NULL,
                    dst_mac TEXT,
                    bssid TEXT,
                    ssid TEXT,
                    seq INTEGER NOT NULL,
                    type INTEGER NOT NULL,
                    subtype INTEGER NOT NULL,
                    first_time_us INTEGER NOT NULL,
                    last_time_us INTEGER NOT NULL,
                    approx_unix_time_us INTEGER NOT NULL,
                    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (measurement_id) REFERENCES measurements(id),
                    FOREIGN KEY (window_id) REFERENCES windows(id),
                    FOREIGN KEY (observation_id) REFERENCES ap_observations(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS event_packets (
                    event_id INTEGER NOT NULL,
                    packet_id INTEGER NOT NULL,
                    PRIMARY KEY (event_id, packet_id),
                    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
                    FOREIGN KEY (packet_id) REFERENCES packets(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ap_observations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    measurement_id INTEGER NOT NULL,
                    window_id INTEGER NOT NULL,
                    bssid TEXT NOT NULL,
                    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(window_id, bssid),
                    FOREIGN KEY (measurement_id) REFERENCES measurements(id),
                    FOREIGN KEY (window_id) REFERENCES windows(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS observation_csi_packets (
                    observation_id INTEGER NOT NULL,
                    csi_packet_id INTEGER NOT NULL,
                    role TEXT,
                    PRIMARY KEY (observation_id, csi_packet_id),
                    FOREIGN KEY (observation_id) REFERENCES ap_observations(id) ON DELETE CASCADE,
                    FOREIGN KEY (csi_packet_id) REFERENCES csi_packets(id) ON DELETE CASCADE
                )
            """)


if __name__ == "__main__":
    init_db()