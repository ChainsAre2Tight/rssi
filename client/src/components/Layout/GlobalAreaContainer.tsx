import { useAppStore } from "../../store/useAppStore"
import GlobalTimeline from "../Timeline/GlobalTimeline"
import MapView from "../../map/components/MapView"
import MapToggle from "./MapToggle"
import styles from "./GlobalAreaContainer.module.css"
import WhitelistView from "../WhitelistView/WhitelistView"

export default function GlobalAreaContainer() {
    const localizationMode = useAppStore(s => s.localization.mode)

    let selectedView = null
    switch (localizationMode) {
        case "timeline":    selectedView = <GlobalTimeline />; break;
        case "map":         selectedView = <MapView />;        break;
        case "whitelist":   selectedView = <WhitelistView />;  break;
        default:            selectedView = <div>Invalid state</div>
    }

    return (
        <div className={styles.root}>
            {selectedView}

            <div className={styles.toggleContainer}>
                <MapToggle />
            </div>
        </div>
    )
}