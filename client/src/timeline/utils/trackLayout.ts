import { RESIZE_HANDLE_GAP } from "../config"
import type { TimelineLanes, TimelineTrack, TrackLayoutItem } from "../types"

export function computeTrackLayout(
    tracks: TimelineTrack[],
    itemsByTrack: Record<string, TimelineLanes>,
): TrackLayoutItem[] {
    const result: TrackLayoutItem[] = []

    let currentY = 0

    for (const track of tracks) {
        const baseHeight = track.height

        const contentY = currentY
        
        const laneHeight = 12

        const lanes = itemsByTrack[track.id] || []
        const laneCount = lanes.length

        const contentHeight = laneCount * laneHeight
        const viewportHeight = track.height

        result.push({
            id: track.id,
            y: currentY,
            height: baseHeight,
            contentY,
            contentHeight,
            viewportHeight,
            track,
            laneHeight,
            laneCount,
            scrollY: track.scrollY ?? 0,
        })

        currentY += baseHeight + RESIZE_HANDLE_GAP
    }

    return result
}
