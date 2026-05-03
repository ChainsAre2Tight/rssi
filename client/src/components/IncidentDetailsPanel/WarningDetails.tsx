import { useAppStore } from "../../store/useAppStore"
import { getWarningKey } from "../../utils/warningKey"
import WarningExpandedDetails from "./WarningExpandedDetails"

import styles from "./WarningDetails.module.css"
import { prettifyWarnings } from "../../utils/prettyMapper"

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

    const prettyWarning = prettifyWarnings(warning?.signal)

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
                    {prettyWarning.name}
                </span>

                <span className={`${styles.importance} ${styles[warning.importance]}`}>
                    {warning.importance.toUpperCase()}
                </span>
            </div>

            <div className={styles.body}>
                <WarningExpandedDetails warning={warning} />
            </div>

        </div>
    )
}
