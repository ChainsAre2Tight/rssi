import type { Sensor } from "../../services/localizationApi"
import { useAppStore } from "../../store/useAppStore"
import { SensorHeaderRow } from "./SensorHeaderRow"
import { SensorDescriptionRow } from "./SensorDescriptionRow"
import { SensorPositionRow } from "./SensorPositionRow"

export function SensorBlock({ sensor }: { sensor: Sensor }) {
    const active = useAppStore(s => s.whitelistUI.active)
    const hover = useAppStore(s => s.hover.whitelist)

    const isActive =
        active.sensor === sensor.name &&
        ["sensor", "sensor-desc", "sensor-pos"].includes(active.type ?? "")

    const isHovered =
        hover.sensor === sensor.name &&
        hover.type === "sensor"

    return (
        <>
            <SensorHeaderRow        sensor={sensor} isHovered={isHovered} isSelected={isActive} />
            <SensorDescriptionRow   sensor={sensor} isHovered={isHovered} isSelected={isActive} />
            <SensorPositionRow      sensor={sensor} isHovered={isHovered} isSelected={isActive} />
        </>
    )
}
