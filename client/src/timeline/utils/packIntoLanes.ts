import { SEVERITY_ORDER } from "../../types/general"
import type { TimelineItem, TimelineLanes } from "../types"

interface PackOptions {
    minGap: number
}

export function packIntoLanes(
    events: TimelineItem[],
    { minGap }: PackOptions
): TimelineLanes {
    if (events.length === 0) return []

    // 1. sort by severity DESC, then start ASC
    const sorted = [...events].sort((a, b) => {
        const sevDiff = SEVERITY_ORDER[b.severity] - SEVERITY_ORDER[a.severity]
        if (sevDiff !== 0) return sevDiff
        return a.start - b.start
    })

    const lanes: TimelineLanes = []
    const laneEndTimes: number[] = []

    for (const event of sorted) {
        let placed = false

        for (let i = 0; i < lanes.length; i++) {
            const lastEnd = laneEndTimes[i]

            if (event.start >= lastEnd + minGap) {
                lanes[i].push(event)
                laneEndTimes[i] = event.end
                placed = true
                break
            }
        }

        if (!placed) {
            lanes.push([event])
            laneEndTimes.push(event.end)
        }
    }

    // 2. sort each lane by time (important for binary search later)
    for (const lane of lanes) {
        lane.sort((a, b) => a.start - b.start)
    }

    return lanes
}
