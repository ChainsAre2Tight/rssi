import styles from "./WhitelistView.module.css"

export function SSIDRow({ ssid }: { ssid: string }) {
    return (
        <div className={styles.row}>
            <div className={styles.indent} />

            <div className={styles.icon}>📶</div>

            <div className={styles.chevron}>▼</div>

            <div className={styles.label} title={ssid}>
                {ssid}
            </div>

            <div className={styles.actions}>
                <button className={styles.btn}>✎</button>
                <button className={styles.btn}>🗑</button>
                <button className={styles.btn}>+</button>
            </div>
        </div>
    )
}

export function BSSIDRow({
    bssid
}: {
    bssid: string
}) {
    return (
        <div className={styles.row}>
            <div className={styles.indent} />
            <div className={styles.indent} />

            <div className={styles.icon}>📡</div>

            <div className={styles.chevron} />

            <div className={styles.label} title={bssid}>
                {bssid}
            </div>

            <div className={styles.actions}>
                <button className={styles.btn}>🗑</button>
            </div>
        </div>
    )
}

export function AddSSIDRow() {
    return (
        <div className={`${styles.row} ${styles.addRow}`}>
            <div className={styles.indent} />

            <div className={styles.icon} />

            <div className={styles.chevron} />

            <div className={styles.label}>
                + Add SSID
            </div>
        </div>
    )
}

export function AddBSSIDRow() {
    return (
        <div className={`${styles.row} ${styles.addRow}`}>
            <div className={styles.indent} />
            <div className={styles.indent} />

            <div className={styles.icon} />

            <div className={styles.chevron} />

            <div className={styles.label}>
                + Add BSSID
            </div>
        </div>
    )
}
