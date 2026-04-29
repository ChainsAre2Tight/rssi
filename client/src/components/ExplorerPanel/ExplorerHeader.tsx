import { useAppStore } from "../../store/useAppStore"
import { SEVERITIES, type Incident, type Modality } from "../../types/general"
import styles from "./ExplorerHeader.module.css"

type Props = {
    incidentsByModality: Record<Modality, Incident[]>
    filtered: Record<Modality, Incident[]>
}

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
                    {SEVERITIES.map(sev => (
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
