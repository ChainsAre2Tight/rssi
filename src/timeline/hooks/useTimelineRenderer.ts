import { useEffect } from "react"
import type { RefObject } from "react"
import type { TimelineItem, TrackLayoutItem } from "../types/types"
import { hitTest, timeToX } from "../utils/mapping"

interface Viewport {
    start: number
    end: number
}

interface Params {
    canvasRef: RefObject<HTMLCanvasElement>
    width: number
    height: number
    viewport: Viewport
    cursor: RefObject<{ x: number; y: number } | null>
    zoomAnchorX: RefObject<number | null>
    isZooming: RefObject<boolean>
    getNiceStep: (raw: number) => number
    tracks: TrackLayoutItem[]
    itemsByTrack: Record<string, TimelineItem[][]>
}

export function useTimelineRenderer({
    canvasRef,
    width,
    height,
    viewport,
    cursor,
    zoomAnchorX,
    isZooming,
    getNiceStep,
    tracks,
    itemsByTrack,
}: Params) {
    useEffect(() => {
        let frameId: number

        function render() {
            const canvas = canvasRef.current
            if (!canvas || width === 0 || height === 0) {
                frameId = requestAnimationFrame(render)
                return
            }

            const ctx = canvas.getContext("2d")
            if (!ctx) {
                frameId = requestAnimationFrame(render)
                return
            }

            const dpr = window.devicePixelRatio || 1

            canvas.width = width * dpr
            canvas.height = height * dpr

            ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

            const styles = getComputedStyle(document.documentElement)

            // --- CLEAR ---
            ctx.fillStyle = styles.getPropertyValue("--color-bg")
            ctx.fillRect(0, 0, width, height)

            // --- GRID ---
            const duration = viewport.end - viewport.start
            const scale = width / duration

            const targetPxPerTick = 100
            const rawStep = targetPxPerTick / scale
            const step = getNiceStep(rawStep)

            const firstTick = Math.floor(viewport.start / step) * step

            ctx.strokeStyle = styles.getPropertyValue("--color-border")
            ctx.lineWidth = 1

            for (let t = firstTick; t < viewport.end; t += step) {
                const x = Math.round((t - viewport.start) * scale) + 0.5

                ctx.beginPath()
                ctx.moveTo(x, 0)
                ctx.lineTo(x, height)
                ctx.stroke()
            }

            // --- TRACKS ---
            ctx.strokeStyle = styles.getPropertyValue("--color-border")
            ctx.lineWidth = 1

            for (const t of tracks) {

                const y = Math.round(t.y) + 0.5

                ctx.beginPath()
                ctx.moveTo(0, y)
                ctx.lineTo(width, y)
                ctx.stroke()
            }

            if (tracks.length > 0) {
                const last = tracks[tracks.length - 1]
                const y = Math.round(last.y + last.height) + 0.5

                ctx.beginPath()
                ctx.moveTo(0, y)
                ctx.lineTo(width, y)
                ctx.stroke()
            }

            for (const t of tracks) {
                if (t.contentHeight <= 0) continue

                const lanes = itemsByTrack[t.id]
                if (!lanes) continue

                for (let laneIndex = 0; laneIndex < lanes.length; laneIndex++) {
                    const lane = lanes[laneIndex]

                    for (let i = 0; i < lane.length; i++) {
                        const item = lane[i]

                        const y =
                            t.contentY +
                            laneIndex * t.laneHeight +
                            2

                        const x = (item.start - viewport.start) * scale
                        const w = (item.end - item.start) * scale
                        const h = t.laneHeight - 4

                        ctx.fillStyle = "#4da3ff"

                        ctx.beginPath()
                        ctx.roundRect(x, y, Math.max(w, 4), h, 4)
                        ctx.fill()
                    }
                }

            let hoveredItem: TimelineItem | null = null

            if (cursor.current) {
                hoveredItem = hitTest(
                    cursor.current.x,
                    cursor.current.y,
                    width,
                    viewport,
                    tracks,
                    itemsByTrack,
                )
            }

            if (hoveredItem !== null) {

                const x1 = timeToX(hoveredItem.start, viewport, width)
                const x2 = timeToX(hoveredItem.end, viewport, width)

                ctx.globalAlpha = 0.5
                ctx.setLineDash([8, 8])
                ctx.strokeStyle = styles.getPropertyValue("--color-accent")

                ctx.beginPath()
                ctx.moveTo(x1, 0)
                ctx.lineTo(x1, height)
                ctx.moveTo(x2, 0)
                ctx.lineTo(x2, height)
                ctx.stroke()

                ctx.setLineDash([])
                ctx.globalAlpha = 1
            }

            // --- CURSOR / ANCHOR ---
            if (isZooming.current && zoomAnchorX.current !== null) {
                const x = Math.round(zoomAnchorX.current) + 0.5

                ctx.strokeStyle = styles.getPropertyValue("--color-accent")
                ctx.lineWidth = 2

                ctx.beginPath()
                ctx.moveTo(x, 0)
                ctx.lineTo(x, height)
                ctx.stroke()
            } else if (cursor.current !== null && cursor.current.x !== null) {
                const x = Math.round(cursor.current.x) + 0.5

                ctx.strokeStyle = styles.getPropertyValue("--color-accent")
                ctx.lineWidth = 1

                ctx.beginPath()
                ctx.moveTo(x, 0)
                ctx.lineTo(x, height)
                ctx.stroke()
            }

            frameId = requestAnimationFrame(render)
        }
    }
        frameId = requestAnimationFrame(render)

        return () => cancelAnimationFrame(frameId)
    }, [width, height, viewport, canvasRef, tracks])
}
