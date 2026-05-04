import type { Sensor } from "../../services/localizationApi"
import { useAppStore } from "../../store/useAppStore"
import styles from "./WhitelistView.module.css"

export function SensorRow({
    sensor,
}: {
    sensor: Sensor,
}) {
    return (
        <div>
            {sensor.name} {sensor.x} {sensor.y} {sensor.z}
        </div>
    )
}