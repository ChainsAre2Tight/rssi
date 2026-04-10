import { useState } from "react"
import type { Warning } from "../../types/general"
import { getSignalLabel } from "../../features/warnings/singalLabels"
import { useAppStore } from "../../store/useAppStore"

import WarningExpandedDetails from "./WarningExpandedDetails"

import styles from "./WarningRow.module.css"

interface Props {
    warning: Warning
    incidentId: string
}

export default function WarningRow({ warning, incidentId }: Props) {

    const [expanded, setExpanded] = useState(false)

    const selectWarning = useAppStore(s => s.selectWarning)

    const key = `${incidentId}:${warning.signal}`

    return (

        <div className={`${styles.row} ${styles[warning.severity]}`}>

            <div
                className={styles.summary}
                onClick={() => {
                    setExpanded(v => !v)
                    selectWarning(key)
                }}
            >

                <span className={styles.arrow}>
                    {expanded ? "▼" : "▶"}
                </span>

                <span className={styles.label}>
                    {getSignalLabel(warning.signal)}
                </span>

                <span className={styles.count}>
                    ({warning.occurrences.length})
                </span>

            </div>

            {expanded && (
                <WarningExpandedDetails warning={warning} />
            )}

        </div>
    )
}