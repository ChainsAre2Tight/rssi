import { RESIZE_HANDLE_GAP } from "../config"
import type { TimelineTrack, TrackLayoutItem } from "../types"

export function computeTrackLayout(
    tracks: TimelineTrack[]
): TrackLayoutItem[] {
    const result: TrackLayoutItem[] = []

    let currentY = 0

    for (const track of tracks) {
        const baseHeight = track.height

        const contentY = currentY

        const contentHeight = Math.max(0, baseHeight)
        
        const laneHeight = 12
        const laneCount = Math.max(1, Math.floor(contentHeight / laneHeight))

        result.push({
            id: track.id,
            y: currentY,
            height: baseHeight,
            contentY,
            contentHeight,
            track,
            laneHeight,
            laneCount,
        })

        currentY += baseHeight + RESIZE_HANDLE_GAP
    }

    return result
}
