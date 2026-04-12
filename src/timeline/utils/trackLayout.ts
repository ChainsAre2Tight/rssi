import type { TimelineTrack, TrackLayoutItem } from "../types/types"

const HEADER_HEIGHT = 28
const RESIZE_HANDLE_GAP = 6

export function computeTrackLayout(
    tracks: TimelineTrack[]
): TrackLayoutItem[] {
    const result: TrackLayoutItem[] = []

    let currentY = 0

    for (const track of tracks) {
        const isCollapsed = track.height <= HEADER_HEIGHT

        const baseHeight = track.height

        const contentY = isCollapsed
            ? 0
            : currentY + HEADER_HEIGHT + RESIZE_HANDLE_GAP

        const contentHeight = isCollapsed
            ? 0
            : Math.max(
                0,
                baseHeight - HEADER_HEIGHT - RESIZE_HANDLE_GAP
            )
        
        const laneHeight = 24
        const laneCount = isCollapsed
            ? 0
            : Math.max(1, Math.floor(contentHeight / laneHeight))

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

        currentY += baseHeight
    }

    return result
}
