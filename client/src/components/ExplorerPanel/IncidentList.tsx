import type { Incident, Modality } from "../../types/general"

import IncidentRow from "./IncidentRow"

type Props = {
    modality: Modality
    incidents: Incident[]
}

export default function IncidentList({
    modality,
    incidents
}: Props) {

    const sorted = [...incidents].sort((a, b) => {

        const sevOrder = {
            critical: 5,
            high: 4,
            medium: 3,
            low: 2,
            info: 1
        }

        const sevDiff =
            sevOrder[b.severity] -
            sevOrder[a.severity]

        if (sevDiff !== 0) return sevDiff

        return a.startTimeUs - b.startTimeUs
    })

    return (
        <>
            {sorted.map((incident) => (
                <IncidentRow
                    key={incident.id}
                    modality={modality}
                    incident={incident}
                />
            ))}
        </>
    )
}
