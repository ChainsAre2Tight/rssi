import { useAppStore } from "../../store/useAppStore"
import VerticalResizer from "../Layout/VerticalResizer"
import { AddBSSIDRow } from "./AddBSSIDRow"
import { AddSSIDRow } from "./AddSSIDRow"
import { BSSIDRow } from "./BSSIDRow"
import { MeasurementHeader } from "./MeasurementHeader"
import { SensorEditor } from "./SensorEditor"
import { SSIDRow } from "./SSIDRow"
import styles from "./WhitelistView.module.css"

export default function WhitelistView() {
    const measurementId = useAppStore(s => s.context.measurementId)
    const whitelist = useAppStore(s =>
        measurementId ? s.whitelist.byMeasurement[measurementId] : undefined
    )

    const whitelistWidth = useAppStore(
        (s) => s.layout.whitelistWidth
    )

    const setLayout = useAppStore((s) => s.setLayout)

    function resize(delta: number) {
        setLayout((prev) => ({
            ...prev,
            whitelistWidth: Math.max(
                200,
                prev.whitelistWidth + delta
            )
        }))
    }

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

            <div className={styles.horizontalContainer}>

                {/* Tree */}
                <div className={styles.tree} style={{width: whitelistWidth}}>
                    {ssids.map(ssid => (
                        <SSIDGroup
                            key={ssid}
                            ssid={ssid}
                            bssids={Object.keys(whitelist[ssid] || {})}
                        />
                    ))}
                    <AddSSIDRow />
                </div>

                <VerticalResizer onDrag={resize} />

                <div className={styles.sensorEditor}>
                    <SensorEditor />
                </div>
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