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
