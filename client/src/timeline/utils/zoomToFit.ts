import type { TimelineAdapterResult } from "../types"

export function computeItemsBounds(adapter: TimelineAdapterResult) {
    let min = Infinity
    let max = -Infinity

    for (const trackId of adapter.trackIds) {
        const lanes = adapter.itemsByTrack[trackId]
        if (!lanes) continue

        for (const lane of lanes) {
            for (const item of lane) {
                if (item.start < min) min = item.start
                if (item.end > max) max = item.end
            }
        }
    }

    if (min === Infinity || max === -Infinity) {
        return null
    }

    return { start: min, end: max }
}