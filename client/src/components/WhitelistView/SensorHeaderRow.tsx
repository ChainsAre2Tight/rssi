import { useAppStore } from "../../store/useAppStore"
import { TRail } from "./Rail"
import styles from "./WhitelistView.module.css"
import type { Sensor } from "../../services/localizationApi"

export function SensorHeaderRow({
    sensor,
    isHovered,
    isSelected,
}: {
    sensor: Sensor,
    isHovered: boolean,
    isSelected: boolean,
}) {
    const setActive = useAppStore(s => s.setWhitelistActive)
    const hoverWhitelist = useAppStore(s => s.hoverWhitelist)

    return (
        <div
            className={styles.row}
            onClick={(e) => {
                e.stopPropagation()
                setActive({
                    type: "sensor",
                    sensor: sensor.name,
                    ssid: null,
                    bssid: null,
                })
            }}
            onMouseEnter={() =>
                hoverWhitelist({
                    type: "sensor",
                    sensor: sensor.name,
                    ssid: null,
                    bssid: null,
                })
            }
            data-hovered={isHovered}
            data-selected={isSelected}
            onMouseLeave={() => hoverWhitelist(null)}
        >
            <TRail />

            <div className={styles.label}>
                <strong title={sensor.name}>{sensor.name}</strong>
            </div>
        </div>
    )
}
