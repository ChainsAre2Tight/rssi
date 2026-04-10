import type { Warning } from "../../types/general"
import { formatOccurrenceRange } from "../../utils/time"

import styles from "./WarningExpandedDetails.module.css"

interface Props {
    warning: Warning
}

function renderMetadataValue(value: any) {

    if (value === null || value === undefined) return "-"

    if (typeof value === "object") {
        return Object.entries(value)
            .map(([k,v]) => `${k}: ${String(v)}`)
            .join(", ")
    }

    return String(value)
}

export default function WarningExpandedDetails({ warning }: Props) {

    return (

        <div className={styles.details}>

            <div className={styles.block}>
                Detector:
                <span className={styles.value}>{warning.type}</span>
            </div>

            <div className={styles.block}>
                Severity:
                <span className={`${styles.severity} ${styles[warning.severity]}`}>
                    {warning.severity.toUpperCase()}
                </span>
            </div>

            {Object.keys(warning.metadata).length > 0 && (
                <div className={styles.block}>

                    Metadata:

                    <div className={styles.metadataList}>
                        {Object.entries(warning.metadata).map(([k,v]) => (
                            <div key={k} className={styles.metadataRow}>
                                <span className={styles.key}>{k}</span>
                                <span className={styles.value}>
                                    {renderMetadataValue(v)}
                                </span>
                            </div>
                        ))}
                    </div>

                </div>
            )}

            <div className={styles.block}>

                Occurrences:

                <div className={styles.occurrenceList}>
                    {warning.occurrences.map((o,i) => (
                        <div key={i} className={styles.occurrenceRow}>
                            {formatOccurrenceRange(o.startTimeUs, o.endTimeUs)}
                        </div>
                    ))}
                </div>

            </div>

        </div>
    )
}