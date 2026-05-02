import { useAppStore } from "../../store/useAppStore"
import { AddBSSIDRow } from "./AddBSSIDRow"
import { AddSSIDRow } from "./AddSSIDRow"
import { BSSIDRow } from "./BSSIDRow"
import { MeasurementHeader } from "./MeasurementHeader"
import { SSIDRow } from "./SSIDRow"
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
                <MeasurementHeader />
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
                    ssid={ssid}
                    bssid={bssid}
                />
            ))}

            <AddBSSIDRow ssid={ssid} />
        </>
    )
}