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
                    whitelist_json TEXT,
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
                    stage INTEGER NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    processing_started_at INTEGER,
                    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(measurement_id, layer, sequence_id),
                    UNIQUE(measurement_id, layer, start_time_us),
                    FOREIGN KEY (measurement_id) REFERENCES measurements(id)
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_windows_measurement_status_time
                ON windows(measurement_id, status, end_time_us)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_windows_stage_status
                ON windows(measurement_id, stage, status)
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
                CREATE INDEX IF NOT EXISTS idx_events_window
                ON events(window_id)
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
                CREATE INDEX IF NOT EXISTS idx_event_packets_packet
                ON event_packets(packet_id)
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

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS detection_signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    measurement_id INTEGER NOT NULL,
                    window_id INTEGER NOT NULL,

                    start_time_us INTEGER NOT NULL,
                    end_time_us INTEGER NOT NULL,

                    observation_id INTEGER,

                    bssid TEXT NOT NULL,
                    ssid TEXT,

                    detector TEXT NOT NULL,
                    signal TEXT NOT NULL,
                    severity TEXT NOT NULL,

                    metadata_json TEXT,

                    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (measurement_id) REFERENCES measurements(id),
                    FOREIGN KEY (window_id) REFERENCES windows(id),
                    FOREIGN KEY (observation_id) REFERENCES ap_observations(id)
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_detection_signals_window
                ON detection_signals(window_id);
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_detection_signals_measurement_time
                ON detection_signals(measurement_id, start_time_us);
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_detection_signals_bssid
                ON detection_signals(bssid);
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS localization_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    measurement_id INTEGER NOT NULL,
                    window_id INTEGER NOT NULL,
                    bssid TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending', -- pending | processing | done
                    processing_started_at INTEGER,
                    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(window_id, bssid)
                    FOREIGN KEY (measurement_id) REFERENCES measurements(id),
                    FOREIGN KEY (window_id) REFERENCES windows(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS localization_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    measurement_id INTEGER NOT NULL,
                    window_id INTEGER NOT NULL,
                    bssid TEXT NOT NULL,
                    start_time_us INTEGER NOT NULL,
                    end_time_us INTEGER NOT NULL,
                    x REAL NOT NULL,
                    y REAL NOT NULL,
                    z REAL NOT NULL,
                    estimated_p0 REAL,
                    device_count INTEGER,
                    converged BOOLEAN,
                    is_calibrated BOOLEAN NOT NULL,
                    metadata_json TEXT,
                    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(window_id, bssid),
                    FOREIGN KEY (measurement_id) REFERENCES measurements(id),
                    FOREIGN KEY (window_id) REFERENCES windows(id)
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_localization_jobs_status
                ON localization_jobs(status)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_localization_jobs_window
                ON localization_jobs(window_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_localization_results_bssid_time
                ON localization_results(bssid, start_time_us)
            """)



if __name__ == "__main__":
    init_db()