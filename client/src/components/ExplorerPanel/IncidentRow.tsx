import { useAppStore } from "../../store/useAppStore"

import type { Incident, Modality } from "../../types/general"

import IdentityLabel from "./IdentityLabel"
import SeverityDot from "./SeverityDot"

import styles from "./ExplorerPanel.module.css"
import { useEffect, useRef } from "react"

type Props = {
    modality: Modality
    incident: Incident
}

export default function IncidentRow({
    modality,
    incident
}: Props) {

    const selectIncident = useAppStore((s) => s.selectIncident)
    const alreadySelected = useAppStore((s) => s.selection.incidentId)
    const hoverIncident = useAppStore((s) => s.hoverIncident)

    const selected = useAppStore(
        (s) => s.selection.incidentId === incident.id
    )

    const hovered = useAppStore(
        (s) => s.hover.incidentId === incident.id
    )

    const reportStart = useAppStore(s => s.report.startTimeUs)
    const reportEnd = useAppStore(s => s.report.endTimeUs)

    const duration = incident.endTimeUs - incident.startTimeUs
    const total = reportEnd && reportStart ? reportEnd - reportStart : 1

    const ratio = Math.min(duration / total, 1)

    const rowRef = useRef<HTMLDivElement | null>(null)

    useEffect(() => {
        if (selected) {
            rowRef.current?.scrollIntoView({
                block: "nearest",
                behavior: "smooth",
            })
        }
    }, [selected])

    return (

        <div
            ref={rowRef}
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
                selectIncident(incident.id === alreadySelected ? null : incident.id)
            }
        >

            <SeverityDot severity={incident.severity} />

            <IdentityLabel
                modality={modality}
                identity={incident.identity}
            />

            <div className={styles.durationBarContainer}>
                <div
                    className={styles.durationBar}
                    style={{ width: `${ratio * 100}%` }}
                />
            </div>

        </div>

    )
}
