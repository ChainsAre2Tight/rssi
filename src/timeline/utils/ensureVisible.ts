import type { Viewport } from "../types"

interface EnsureVisibleParams {
    viewport: Viewport
    itemStart: number
    itemEnd: number
    paddingRatio?: number // 0.1 = 10%
}

export function ensureVisible({
    viewport,
    itemStart,
    itemEnd,
    paddingRatio = 0.1,
}: EnsureVisibleParams): Viewport {
    const duration = viewport.end - viewport.start
    const padding = duration * paddingRatio

    const paddedStart = viewport.start + padding
    const paddedEnd = viewport.end - padding

    const itemDuration = itemEnd - itemStart

    // fully visible with padding
    if (itemStart >= paddedStart && itemEnd <= paddedEnd) {
        return viewport
    }

    // item larger than viewport is centered
    if (itemDuration > duration) {
        const center = (itemStart + itemEnd) / 2
        return {
            start: center - duration / 2,
            end: center + duration / 2,
        }
    }

    // shift minimally
    let newStart = viewport.start
    let newEnd = viewport.end

    if (itemStart < paddedStart) {
        const delta = paddedStart - itemStart
        newStart -= delta
        newEnd -= delta
    } else if (itemEnd > paddedEnd) {
        const delta = itemEnd - paddedEnd
        newStart += delta
        newEnd += delta
    }

    return { start: newStart, end: newEnd }
}