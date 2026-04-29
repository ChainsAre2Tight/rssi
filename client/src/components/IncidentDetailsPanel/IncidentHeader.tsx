import { useAppStore } from "../../store/useAppStore"
import { formatDateTime } from "../../utils/time"
import LocalizationButtons from "./LocalizationButtons"

import styles from "./IncidentHeader.module.css"
import WhitelistButtons from "./WhitelistButtons"

export default function IncidentHeader() {

    const incidentId = useAppStore(s => s.selection.incidentId)
    const incidentsByModality = useAppStore(s => s.report.incidentsByModality)

    const incident = Object.values(incidentsByModality)
        .flat()
        .find(i => i.id === incidentId)

    if (!incident) {
        return (
            <div className={styles.root}>
                No incident selected
            </div>
        )
    }

    const identity =
        incident.identity
            ? Object.values(incident.identity).join(" ")
            : incident.id

    return (
        <div className={styles.root}>

            <div className={styles.left}>
                <span className={`${styles.dot} ${styles[incident.severity]}`} />
                <span className={styles.identity}>{identity}</span>
            </div>

            <div className={styles.center}>
                {formatDateTime(incident.startTimeUs)}
                {" — "}
                {formatDateTime(incident.endTimeUs)}
            </div>

            <div className={styles.right}>
                <WhitelistButtons />
                <div className={styles.separator} />
                <LocalizationButtons />
            </div>

        </div>
    )
}