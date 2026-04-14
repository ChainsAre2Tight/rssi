import type { Incident, Modality, Severity } from "../types/general"

export function filterIncidents(
    incidentsByModality: Record<Modality, Incident[]>,
    severityFilter: Record<Severity, boolean>
) {
    const result: Record<Modality, Incident[]> = {
        logical: [],
        physical: [],
    }

    for (const modality of Object.keys(incidentsByModality) as Modality[]) {
        result[modality] = incidentsByModality[modality].filter(
            (inc) => severityFilter[inc.severity]
        )
    }

    return result
}