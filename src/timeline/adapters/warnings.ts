import type { Incident } from "../../types/general"

import type {
    TimelineItem,
    TimelineAdapterResult
} from "../types"

import { SEVERITY_ORDER } from "../../types/general"

interface Params {
    incident: Incident
}

export function buildWarningAdapter({
    incident,
}: Params): TimelineAdapterResult {
    const itemsByTrack: Record<string, TimelineItem[][]> = {}

    const byKey = new Map<string, TimelineItem>()
    const byId = new Map<string, TimelineItem>()

    const trackId = "warnings"
    const trackIds = [trackId]

    // 🔹 sort warnings by severity DESC
    const sortedWarnings = [...incident.warnings].sort(
        (a, b) => SEVERITY_ORDER[b.severity] - SEVERITY_ORDER[a.severity]
    )

    const lanes: TimelineItem[][] = []

    for (const warning of sortedWarnings) {
        const lane: TimelineItem[] = []

        const key = `${incident.id}:${warning.signal}`

        // 🔹 occurrences → items in SAME lane
        for (const occ of warning.occurrences) {
            const item: TimelineItem = {
                id: key, // same id for all segments
                key,
                type: "warning",

                start: occ.startTimeUs / 1_000_000,
                end: occ.endTimeUs / 1_000_000,

                severity: warning.severity,
            }

            lane.push(item)
        }

        // 🔹 sort occurrences in lane (just in case)
        lane.sort((a, b) => a.start - b.start)

        // 🔹 index (only once per warning is enough, but harmless to overwrite)
        if (lane.length > 0) {
            byKey.set(key, lane[0])
            byId.set(key, lane[0])
        }

        lanes.push(lane)
    }

    itemsByTrack[trackId] = lanes

    return {
        itemsByTrack,
        index: {
            byKey,
            byId,
        },
        bounds: {
            start: incident.startTimeUs,
            end: incident.endTimeUs,
        },
        trackIds,
    }
}