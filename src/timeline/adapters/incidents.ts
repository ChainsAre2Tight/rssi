import type {
    Incident,
    Modality,
    Severity
} from "../../types/general"

import type {
    TimelineItem,
    TimelineAdapterResult
} from "../types"

import { packIntoLanes } from "../utils/packIntoLanes"

interface Params {
    incidentsByModality: Record<Modality, Incident[]>
    reportStartUs: number
    reportEndUs: number
    minGapUs?: number
}

export function buildIncidentAdapter({
    incidentsByModality,
    reportStartUs,
    reportEndUs,
    minGapUs = 0,
}: Params): TimelineAdapterResult {
    const itemsByTrack: Record<string, TimelineItem[][]> = {}

    const byKey = new Map<string, TimelineItem>()
    const byId = new Map<string, TimelineItem>()

    for (const modality of Object.keys(incidentsByModality) as Modality[]) {
        const incidents = incidentsByModality[modality]

        const events: TimelineItem[] = incidents.map((inc) => {
            const event: TimelineItem = {
                id: inc.id,
                key: inc.id,
                type: "incident",

                start: inc.startTimeUs,
                end: inc.endTimeUs,

                severity: inc.severity,
            }

            byKey.set(event.key, event)
            byId.set(event.id, event)

            return event
        })

        const lanes = packIntoLanes(events, {
            minGap: minGapUs,
        })

        itemsByTrack[modality] = lanes
    }

    console.log(reportStartUs, reportEndUs)

    return {
        itemsByTrack,
        index: {
            byKey,
            byId,
        },
        bounds: {
            start: reportStartUs,
            end: reportEndUs,
        },
    }
}
