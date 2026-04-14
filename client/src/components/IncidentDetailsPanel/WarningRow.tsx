import { useEffect, useRef } from "react"
import { useAppStore } from "../../store/useAppStore"
import type { Warning } from "../../types/general"
import { getWarningKey } from "../../utils/warningKey"
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

    const selectedKey = useAppStore(s => s.selection.warningKey)
    const key = getWarningKey(warning)

    const isSelected = key === selectedKey

    const rowRef = useRef<HTMLDivElement | null>(null)

    useEffect(() => {
        if (isSelected) {
            rowRef.current?.scrollIntoView({
                block: "nearest",
                behavior: "smooth",
            })
        }
    }, [isSelected])

    return (
        <div className={`${styles.row} ${styles[warning.severity]}`} ref={rowRef}>

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