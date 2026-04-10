import type { Incident, Modality } from "../../types/general"
import type { BackendReport } from "../../types/backend"


export function adaptReport(api: BackendReport) {
    const result: Record<Modality, Incident[]> = {
        logical: [],
        physical: [],
        // ml: []
    }

    let incidentCounter = 0

    for (const modalityKey in api.modalities) {
        const modality = modalityKey as Modality

        const incidents = api.modalities[modality] || []

        result[modality] = incidents.map((inc) => {
            incidentCounter++

            return {
                id: `${modality}-${incidentCounter}`,

                modality,

                startTimeUs: inc.start_time_us,
                endTimeUs: inc.end_time_us,

                severity: inc.severity,

                identity: inc.identity ?? null,

                warnings: inc.warnings.map((w) => ({
                    type: w.signal,
                    severity: w.severity,
                    signal: w.signal,
                    metadata: w.metadata,
                    occurrences: w.occurrences.map((o) => ({
                        startTimeUs: o.start_time_us,
                        endTimeUs: o.end_time_us
                    }))
                }))
            }
        })
    }

    return {
        startTimeUs: null,
        endTimeUs: api.end_time_us,
        incidentsByModality: result
    }
}