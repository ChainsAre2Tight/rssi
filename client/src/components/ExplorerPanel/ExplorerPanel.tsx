import { useAppStore } from "../../store/useAppStore"
import ModalitySection from "./ModalitySection"
import styles from "./ExplorerPanel.module.css"
import { filterIncidents } from "../../utils/filterIncidents"
import ExplorerHeader from "./ExplorerHeader"

export default function ExplorerPanel() {

    const incidentsByModality = useAppStore(
        (s) => s.report.incidentsByModality
    )

    const severityFilter = useAppStore(
        (s) => s.filters.severities
    )

    const filtered = filterIncidents(
        incidentsByModality,
        severityFilter
    )

    const total =
        incidentsByModality.logical.length +
        incidentsByModality.physical.length

    if (total === 0) {
        return (
            <div className={styles.empty}>
                No incidents detected in this report.
            </div>
        )
    }

    return (
        <div className={styles.root}>

            <ExplorerHeader
                incidentsByModality={incidentsByModality}
                filtered={filtered}
            />

            <ModalitySection
                modality="logical"
                incidents={filtered.logical}
                totalCount={incidentsByModality.logical.length}
            />

            <ModalitySection
                modality="physical"
                incidents={filtered.physical}
                totalCount={incidentsByModality.physical.length}
            />

        </div>
    )
}