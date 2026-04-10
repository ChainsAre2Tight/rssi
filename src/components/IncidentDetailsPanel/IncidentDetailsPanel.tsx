import IncidentHeader from "./IncidentHeader"
import WarningTimeline from "./WarningTimeline"
import WarningDetailsList from "./WarningDetailsList"

import styles from "./IncidentDetailsPanel.module.css"

export default function IncidentDetailsPanel() {

    return (

        <div className={styles.root}>

            <IncidentHeader />

            <WarningTimeline />

            <WarningDetailsList />

        </div>

    )
}
