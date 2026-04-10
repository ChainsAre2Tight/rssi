import { useAppStore } from "../../store/useAppStore"

import type { Incident, Modality } from "../../types/general"

import IdentityLabel from "./IdentityLabel"
import SeverityDot from "./SeverityDot"

import styles from "./ExplorerPanel.module.css"

type Props = {
    modality: Modality
    incident: Incident
}

export default function IncidentRow({
    modality,
    incident
}: Props) {

    const selectIncident = useAppStore((s) => s.selectIncident)
    const hoverIncident = useAppStore((s) => s.hoverIncident)

    const selected = useAppStore(
        (s) => s.selection.incidentId === incident.id
    )

    const hovered = useAppStore(
        (s) => s.hover.incidentId === incident.id
    )

    return (

        <div
            className={styles.row}
            data-selected={selected}
            data-hovered={hovered}

            onMouseEnter={() =>
                hoverIncident(incident.id)
            }

            onMouseLeave={() =>
                hoverIncident(null)
            }

            onClick={() =>
                selectIncident(incident.id)
            }
        >

            <SeverityDot severity={incident.severity} />

            <IdentityLabel
                modality={modality}
                identity={incident.identity}
            />

            <div className={styles.durationPlaceholder} />

        </div>

    )
}
