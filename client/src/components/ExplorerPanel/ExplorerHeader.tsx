import { useAppStore } from "../../store/useAppStore"
import type { Incident, Modality } from "../../types/general"
import styles from "./ExplorerHeader.module.css"

type Props = {
    incidentsByModality: Record<Modality, Incident[]>
    filtered: Record<Modality, Incident[]>
}

const severities = ["critical", "high", "medium", "low", "info"] as const

export default function ExplorerHeader({
    incidentsByModality,
    filtered,
}: Props) {

    const toggleSeverity = useAppStore(s => s.toggleSeverity)
    const active = useAppStore(s => s.filters.severities)

    const total =
        incidentsByModality.logical.length +
        incidentsByModality.physical.length

    const shown =
        filtered.logical.length +
        filtered.physical.length

    return (
        <div className={styles.root}>

            {/* LEFT */}
            <div className={styles.left}>
                {shown} / {total} incidents
            </div>

            {/* RIGHT */}
            <div className={styles.right}>

                <span className={styles.filtersLabel}>
                    Filters:
                </span>

                <div className={styles.dots}>
                    {severities.map(sev => (
                        <div
                            key={sev}
                            className={styles.dot}
                            data-active={active[sev]}
                            data-severity={sev}
                            onClick={() => toggleSeverity(sev)}
                            title={sev}
                        />
                    ))}
                </div>

            </div>

        </div>
    )
}
