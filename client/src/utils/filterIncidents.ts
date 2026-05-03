import type { Incident, Modality, Importance } from "../types/general"

export function filterIncidents(
    incidentsByModality: Record<Modality, Incident[]>,
    importanceFilter: Record<Importance, boolean>,
    query: string
) {
    const result: Record<Modality, Incident[]> = {
        logical: [],
        physical: [],
    }

    const q = query.trim().toLowerCase()

    function matchesSearch(incident: Incident): boolean {
        if (!q || q === "") return true

        const parts: string[] = []

        // incident basics
        parts.push(incident.id)
        parts.push(incident.modality)

        // identity
        if (incident.identity) {
            for (const value of Object.values(incident.identity)) {
                if (value != null) {
                    parts.push(String(value))
                }
            }
        }

        // warnings
        for (const w of incident.warnings) {
            parts.push(w.signal)
            parts.push(w.type)
        }

        const text = parts.join(" ").toLowerCase()
        return text.includes(q)
    }

    for (const modality of Object.keys(incidentsByModality) as Modality[]) {
        result[modality] = incidentsByModality[modality].filter(
            (inc) =>
                importanceFilter[inc.importance] && matchesSearch(inc)
        )
    }

    return result
}