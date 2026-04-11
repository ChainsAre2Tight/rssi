import type { TimelineTrack } from "../types/types"

export interface TrackLayoutItem {
    id: string
    y: number
    height: number
    contentY: number
    contentHeight: number
    track: TimelineTrack
}

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

        result.push({
            id: track.id,
            y: currentY,
            height: baseHeight,
            contentY,
            contentHeight,
            track,
        })

        currentY += baseHeight
    }

    return result
}
