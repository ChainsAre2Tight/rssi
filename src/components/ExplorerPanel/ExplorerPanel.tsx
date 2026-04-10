import { useAppStore } from "../../store/useAppStore"

import ModalitySection from "./ModalitySection"

import styles from "./ExplorerPanel.module.css"

export default function ExplorerPanel() {

    const incidentsByModality = useAppStore(
        (s) => s.report.incidentsByModality
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

            <ModalitySection
                modality="logical"
                incidents={incidentsByModality.logical}
            />

            <ModalitySection
                modality="physical"
                incidents={incidentsByModality.physical}
            />

        </div>
    )
}