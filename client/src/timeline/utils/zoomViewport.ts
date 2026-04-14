import type { Viewport } from "../types"
import { MIN_DURATION } from "../config"

interface ZoomParams {
    viewport: Viewport
    zoomFactor: number // >1 zoom out, <1 zoom in
    anchorTime?: number // if not provided use center
}

export function zoomViewport({
    viewport,
    zoomFactor,
    anchorTime,
}: ZoomParams): Viewport {

    const duration = viewport.end - viewport.start

    const anchor =
        anchorTime ?? (viewport.start + duration / 2)

    let newDuration = duration * zoomFactor
    newDuration = Math.max(newDuration, MIN_DURATION)

    const ratio = (anchor - viewport.start) / duration

    const newStart = anchor - ratio * newDuration
    const newEnd = newStart + newDuration

    return {
        start: newStart,
        end: newEnd,
    }
}
