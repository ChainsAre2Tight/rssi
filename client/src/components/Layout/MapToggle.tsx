import { useAppStore } from "../../store/useAppStore"
import styles from "./MapToggle.module.css"

export default function MapToggle() {
    const localizationMode = useAppStore((s) => s.localization.mode)
    const setLocalizationMode = useAppStore((s) => s.setLocalizationMode)
    // const selectedIncidentId = useAppStore((s) => s.selection.incidentId)

    // Only show toggle when an incident is selected
    // if (!selectedIncidentId) {
    //     return null
    // }

    return (
        <div className={styles.toggle}>
            <button
                data-active={localizationMode === "timeline"}
                onClick={() => setLocalizationMode("timeline")}
            >
                Timeline
            </button>

            <button
                data-active={localizationMode === "map"}
                onClick={() => setLocalizationMode("map")}
            >
                Map
            </button>
        </div>
    )
}
