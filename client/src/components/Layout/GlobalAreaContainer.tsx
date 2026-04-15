import { useAppStore } from "../../store/useAppStore"
import GlobalTimeline from "../Timeline/GlobalTimeline"
import MapView from "../../map/components/MapView"
import MapToggle from "./MapToggle"
import styles from "./GlobalAreaContainer.module.css"

export default function GlobalAreaContainer() {
    const localizationMode = useAppStore(s => s.localization.mode)

    return (
        <div className={styles.root}>
            {localizationMode === "timeline" ? (
                <GlobalTimeline />
            ) : (
                <MapView />
            )}

            <div className={styles.toggleContainer}>
                <MapToggle />
            </div>
        </div>
    )
}