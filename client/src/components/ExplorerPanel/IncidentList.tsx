import { IMPORTANCE_ORDER, type Incident, type Modality } from "../../types/general"
import { getIncidentDurationUs } from "../../utils/duration"

import IncidentRow from "./IncidentRow"

type Props = {
    modality: Modality
    incidents: Incident[]
    maxDurationUs: number
}

export default function IncidentList({
    modality,
    incidents,
    maxDurationUs,
}: Props) {

    const sorted = [...incidents].sort((a, b) => {

        // 1. importance DESC
        const sevDiff =
            IMPORTANCE_ORDER[b.importance] -
            IMPORTANCE_ORDER[a.importance]

        if (sevDiff !== 0) return sevDiff

        // 2. duration DESC
        const durDiff =
            getIncidentDurationUs(b) -
            getIncidentDurationUs(a)

        if (durDiff !== 0) return durDiff

        // 3. start ASC
        return a.startTimeUs - b.startTimeUs
    })

    return (
        <>
            {sorted.map((incident) => (
                <IncidentRow
                    key={incident.id}
                    modality={modality}
                    incident={incident}
                    maxDurationUs={maxDurationUs}
                />
            ))}
        </>
    )
}
