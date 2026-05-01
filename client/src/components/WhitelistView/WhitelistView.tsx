import { useAppStore } from "../../store/useAppStore"
import { AddBSSIDRow, AddSSIDRow, BSSIDRow, SSIDRow } from "./Rows"
import styles from "./WhitelistView.module.css"

export default function WhitelistView() {
    const measurementId = useAppStore(s => s.context.measurementId)
    const whitelist = useAppStore(s =>
        measurementId ? s.whitelist.byMeasurement[measurementId] : undefined
    )

    if (!measurementId) {
        return <div className={styles.empty}>No measurement selected</div>
    }

    if (!whitelist) {
        return <div className={styles.loading}>Loading whitelist...</div>
    }

    const ssids = Object.keys(whitelist)

    return (
        <div className={styles.root}>
            
            {/* Measurement Header (placeholder for now) */}
            <div className={styles.header}>
                Measurement Header (TODO)
            </div>

            {/* Tree */}
            <div className={styles.tree}>
                {ssids.map(ssid => (
                    <SSIDGroup
                        key={ssid}
                        ssid={ssid}
                        bssids={Object.keys(whitelist[ssid] || {})}
                    />
                ))}

                <AddSSIDRow />
            </div>
        </div>
    )
}

function SSIDGroup({
    ssid,
    bssids
}: {
    ssid: string
    bssids: string[]
}) {
    return (
        <>
            <SSIDRow ssid={ssid} />

            {bssids.map(bssid => (
                <BSSIDRow
                    key={bssid}
                    bssid={bssid}
                />
            ))}

            <AddBSSIDRow />
        </>
    )
}