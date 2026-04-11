import type { TimelineTrack } from "../types/types"

export interface TrackLayoutItem {
    id: string
    y: number
    height: number
    visible: boolean
    track: TimelineTrack
}

export function computeTrackLayout(
    tracks: TimelineTrack[]
): TrackLayoutItem[] {
    const result: TrackLayoutItem[] = []

    let currentY = 0

    for (const track of tracks) {
        const isCollapsed = track.collapsible && track.collapsed

        const height = isCollapsed ? 0 : track.height

        result.push({
            id: track.id,
            y: currentY,
            height,
            visible: height > 0,
            track,
        })

        currentY += height
    }

    return result
}
