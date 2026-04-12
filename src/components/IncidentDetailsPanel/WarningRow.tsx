import type { Warning } from "../../types/general"
import WarningExpandedDetails from "./WarningExpandedDetails"
import styles from "./WarningRow.module.css"

interface Props {
    warning: Warning
    expanded: boolean
    onClick: () => void
}

export default function WarningRow({
    warning,
    expanded,
    onClick,
}: Props) {

    return (
        <div className={`${styles.row} ${styles[warning.severity]}`}>

            <div
                className={styles.summary}
                onClick={onClick}
            >
                <span className={styles.arrow}>
                    {expanded ? "▼" : "▶"}
                </span>

                <span className={styles.label}>
                    {warning.signal}
                </span>

                <span className={styles.count}>
                    {warning.occurrences.length}
                </span>

                <span
                    className={`${styles.severity} ${styles[warning.severity]}`}
                >
                    {warning.severity.toUpperCase()}
                </span>
            </div>

            {expanded && (
                <div className={styles.details}>
                    <WarningExpandedDetails warning={warning} />
                </div>
            )}
        </div>
    )
}