import type { Warning } from "../../types/general"
import { formatOccurrenceRange } from "../../utils/time"

import styles from "./WarningExpandedDetails.module.css"

interface Props {
    warning: Warning
}

export default function WarningExpandedDetails({ warning }: Props) {

    return (

        <div className={styles.details}>

            <div className={styles.block}>
                Detector: {warning.type}
            </div>

            <div className={styles.block}>
                {Object.entries(warning.metadata).map(([k,v]) => (
                    <div key={k}>
                        {k}: {String(v)}
                    </div>
                ))}
            </div>

            <div className={styles.block}>
                Occurrences:
                {warning.occurrences.map((o,i) => (
                    <div key={i}>
                        {formatOccurrenceRange(o.startTimeUs, o.endTimeUs)}
                    </div>
                ))}
            </div>

        </div>
    )
}