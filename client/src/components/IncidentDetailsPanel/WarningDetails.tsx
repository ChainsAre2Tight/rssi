import { useAppStore } from "../../store/useAppStore"
import { getWarningKey } from "../../utils/warningKey"
import WarningExpandedDetails from "./WarningExpandedDetails"

import styles from "./WarningDetails.module.css"

export default function WarningDetails() {

    const incidentId = useAppStore(s => s.selection.incidentId)
    const selectedKey = useAppStore(s => s.selection.warningKey)
    const incidentsByModality = useAppStore(s => s.report.incidentsByModality)

    const incident = Object.values(incidentsByModality)
        .flat()
        .find(i => i.id === incidentId)

    if (!incident || !selectedKey) {
        return (
            <div className={styles.empty}>
                Select a warning to see details
            </div>
        )
    }

    const warning = incident.warnings.find(
        w => getWarningKey(w) === selectedKey
    )

    if (!warning) {
        return (
            <div className={styles.empty}>
                Warning not found
            </div>
        )
    }

    return (
        <div className={styles.root}>

            <div className={styles.header}>
                <span className={styles.title}>
                    {warning.signal}
                </span>

                <span className={`${styles.severity} ${styles[warning.severity]}`}>
                    {warning.severity.toUpperCase()}
                </span>
            </div>

            <div className={styles.body}>
                <WarningExpandedDetails warning={warning} />
            </div>

        </div>
    )
}
