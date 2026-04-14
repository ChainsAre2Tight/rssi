import { useMemo } from "react"
import { useAppStore } from "../../store/useAppStore"
import { getWarningKey } from "../../utils/warningKey"
import styles from "./WarningList.module.css"

const sevOrder = {
    critical: 5,
    high: 4,
    medium: 3,
    low: 2,
    info: 1
}

export default function WarningList() {

    const incidentId = useAppStore(s => s.selection.incidentId)
    const selectedKey = useAppStore(s => s.selection.warningKey)

    const incidentsByModality = useAppStore(s => s.report.incidentsByModality)

    const selectWarning = useAppStore(s => s.selectWarning)
    const hoverWarning = useAppStore(s => s.hoverWarning)

    const incident = Object.values(incidentsByModality)
        .flat()
        .find(i => i.id === incidentId)

    const warnings = useMemo(() => {
        if (!incident) return []

        const duration = incident.endTimeUs - incident.startTimeUs

        return [...incident.warnings]
            .map(w => {
                const total = w.occurrences.reduce(
                    (sum, o) => sum + (o.endTimeUs - o.startTimeUs),
                    0
                )

                return {
                    warning: w,
                    total,
                    ratio: duration > 0 ? total / duration : 0
                }
            })
            .sort((a, b) => {
                const sevDiff =
                    sevOrder[b.warning.severity] -
                    sevOrder[a.warning.severity]

                if (sevDiff !== 0) return sevDiff

                return b.total - a.total
            })

    }, [incident])

    if (!incident) {
        return <div className={styles.empty}>No warnings</div>
    }

    return (
        <div className={styles.root}>

            <div className={styles.scroll}>
                {warnings.map(({ warning, ratio }) => {

                    const key = getWarningKey(warning)
                    const selected = key === selectedKey

                    return (
                        <div
                            key={key}
                            className={styles.row}
                            data-selected={selected}

                            onClick={() => selectWarning(key)}
                            onMouseEnter={() => hoverWarning(key)}
                            onMouseLeave={() => hoverWarning(null)}
                        >

                            <div
                                className={styles.dot}
                                style={{
                                    background: `var(--severity-${warning.severity})`
                                }}
                            />

                            <span
                                className={styles.label}
                                title={warning.signal}
                            >
                                {warning.signal}
                            </span>

                            <div className={styles.durationBarContainer}>
                                <div
                                    className={`${styles.durationBar} ${styles[warning.severity]}`}
                                    style={{
                                        width: `${Math.max(ratio * 100, 2)}%`
                                    }}
                                />
                            </div>

                        </div>
                    )
                })}
            </div>

        </div>
    )
}
