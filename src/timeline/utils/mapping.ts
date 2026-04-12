import type { HitTestResult, TimelineItem, TrackLayoutItem, Viewport } from "../types/types"

function timeFromX(
    x: number,
    width: number,
    viewport: Viewport
) {
    const duration = viewport.end - viewport.start
    return viewport.start + (x / width) * duration
}

function findTrackAtY(
    y: number,
    tracks: TrackLayoutItem[]
): TrackLayoutItem | null {
    for (const t of tracks) {
        if (y >= t.y && y <= t.y + t.height) {
            return t
        }
    }
    return null
}

function findLaneIndex(
    y: number,
    track: TrackLayoutItem
): number | null {
    if (track.contentHeight <= 0) return null

    const relativeY = y - track.contentY
    if (relativeY < 0) return null

    const laneIndex = Math.floor(relativeY / track.laneHeight)

    if (laneIndex >= track.laneCount) return null

    return laneIndex
}

function findItemInLane(
    time: number,
    laneIndex: number,
    trackId: string,
    items: TimelineItem[],
    laneCount: number
): TimelineItem | null {
    const trackItems = items.filter(i => i.trackId === trackId)


    //TODO: use binary search and skip out of viewport bounds
    for (let i = 0; i < trackItems.length; i++) {
        const item = trackItems[i]

        const itemLane = i % laneCount

        if (itemLane !== laneIndex) continue

        if (time >= item.start && time <= item.end) {
            return item
        }
    }

    return null
}

export function hitTest(
    x: number,
    y: number,
    width: number,
    viewport: Viewport,
    tracks: TrackLayoutItem[],
    items: TimelineItem[]
): HitTestResult | null {
    const track = findTrackAtY(y, tracks)
    if (!track) return null

    const laneIndex = findLaneIndex(y, track)
    if (laneIndex === null) return null

    const time = timeFromX(x, width, viewport)

    const item = findItemInLane(
        time,
        laneIndex,
        track.id,
        items,
        track.laneCount
    )

    if (!item) return null

    return {
        item,
        trackId: track.id,
        laneIndex,
    }
}
