import type { TimelineItem, TrackLayoutItem, Viewport } from "../types/types"

export function timeToX(
    time: number,
    viewport: Viewport,
    width: number
) {
    const duration = viewport.end - viewport.start
    return ((time - viewport.start) / duration) * width
}

export function xToTime(
    x: number,
    viewport: Viewport,
    width: number
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
    laneItems: TimelineItem[]
): TimelineItem | null {
    if (laneItems.length === 0) return null
    if (time < laneItems[0].start) return null
    if (time > laneItems[laneItems.length - 1].end) return null

    // binary search by start time
    let left = 0
    let right = laneItems.length - 1

    while (left <= right) {
        const mid = (left + right) >> 1
        const item = laneItems[mid]

        if (item.start > time) {
            right = mid - 1
            continue
        }

        if (item.end < time) {
            left = mid + 1
            continue
        }

        return item
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
): TimelineItem | null {
    const track = findTrackAtY(y, tracks)
    if (!track) return null

    const laneIndex = findLaneIndex(y, track)
    if (laneIndex === null) return null

    const time = xToTime(x, viewport, width)

    const trackItems = items.filter(i => i.trackId === track.id)
    const laneItems = trackItems
        .filter(i => i.laneIndex === laneIndex)
        .filter(i => i.end >= viewport.start && i.start <= viewport.end)
    const item = findItemInLane(
        time,
        laneItems,
    )

    if (!item) return null

    return item
}
