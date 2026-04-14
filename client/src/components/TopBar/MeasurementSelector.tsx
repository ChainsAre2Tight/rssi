import { useAppStore } from "../../store/useAppStore"
import styles from "./TopBar.module.css"

export default function MeasurementSelector() {

    const measurements = useAppStore((s) => s.measurements.items)
    const selectedId = useAppStore((s) => s.context.measurementId)

    const setMeasurement = useAppStore((s) => s.setMeasurement)

    return (
        <select
            className={styles.select}
            value={selectedId ?? ""}
            onChange={(e) => {
                const id = Number(e.target.value)
                setMeasurement(id)
            }}
        >
            <option value="" disabled>
                Select measurement
            </option>

            {measurements.map((m) => (
                <option key={m.id} value={m.id}>
                    {m.name}
                </option>
            ))}
        </select>
    )
}