import { useEffect } from "react"
import type { RefObject } from "react"
import type { TimelineAdapterResult, TimelineItem, TrackLayoutItem, Viewport } from "../types"
import { createTimeMapper, hitTest } from "../utils/mapping"
import { RESIZE_HANDLE_GAP } from "../config"
import { getSeverityColor } from "../../utils/severity"

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
    adapter: TimelineAdapterResult
    selectedItem?: TimelineItem | null
    hoveredItem?: TimelineItem | null
    externalCursorTimeUs?: number | null
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
    adapter,
    selectedItem,
    hoveredItem,
    externalCursorTimeUs
}: Params) {
    useEffect(() => {
        let frameId: number

        function render() {
            let selected = selectedItem
            const canvas = canvasRef.current
            const mapper = createTimeMapper(viewport, width, adapter.bounds.start)
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
            ctx.lineWidth = 3
            ctx.setLineDash([20, 20])

            for (let i = 0; tracks.length > 0 && i < tracks.length; i++) {
                const y = Math.round(tracks[i].y+tracks[i].height) + 0.5
                ctx.beginPath()
                ctx.moveTo(0, y)
                ctx.lineTo(width, y)
                ctx.stroke()
            }

            for (const t of tracks) {
                if (t.contentHeight <= 0) continue

                const lanes = adapter.itemsByTrack[t.id]
                if (!lanes) continue

                ctx.save()
                ctx.beginPath()
                ctx.rect(0, t.contentY-RESIZE_HANDLE_GAP, width, t.contentHeight)
                ctx.clip()

                for (let laneIndex = 0; laneIndex < lanes.length; laneIndex++) {
                    const lane = lanes[laneIndex]

                    const laneTop = t.contentY + laneIndex * t.laneHeight
                    const laneBottom = laneTop + t.laneHeight

                    if (laneTop >= t.contentY + t.contentHeight) {
                        break
                    }
                    if (laneBottom <= t.contentY) {
                        continue
                    }

                    const y = laneTop + 2
                    const h = t.laneHeight - 4

                    for (let i = 0; i < lane.length; i++) {
                        const item = lane[i]

                        if (item.end < viewport.start) continue
                        if (item.start > viewport.end) break

                        const x = mapper.toX(item.start)
                        const w = mapper.toX(item.end) - x

                        if (item === hoveredItem) {
                            ctx.globalAlpha = 0.85
                        } else if (item === selectedItem) {
                            ctx.globalAlpha = 1
                        } else {
                            ctx.globalAlpha = 0.6
                        }

                        ctx.fillStyle = getSeverityColor(item.severity, styles)
                        ctx.beginPath()
                        ctx.roundRect(x, y, Math.max(w, 4), h, 4)
                        ctx.fill()                     
                    }
                }

                ctx.restore()
            }

            if (hoveredItem) {
                const x1 = mapper.toX(hoveredItem.start)
                const x2 = mapper.toX(hoveredItem.end)

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

            if (selected) {
                const x1 = mapper.toX(selected.start)
                const x2 = mapper.toX(selected.end)

                ctx.globalAlpha = 0.05
                ctx.fillStyle = styles.getPropertyValue("--color-accent")
                ctx.fillRect(x1, 0, x2 - x1, height)

                ctx.globalAlpha = 1
                ctx.setLineDash([]) // solid
                ctx.strokeStyle = styles.getPropertyValue("--color-accent")
                ctx.lineWidth = 2

                ctx.beginPath()
                ctx.moveTo(x1, 0)
                ctx.lineTo(x1, height)

                ctx.moveTo(x2, 0)
                ctx.lineTo(x2, height)

                ctx.stroke()
            }

            if (externalCursorTimeUs !== null) {
                
                // idk why that works...
                const mapper = createTimeMapper(viewport, width, 0)
                const x = mapper.toX(
                    mapper.fromGlobalUs(externalCursorTimeUs!)
                )

                ctx.globalAlpha = 0.4
                ctx.setLineDash([4, 4])
                ctx.strokeStyle = styles.getPropertyValue("--color-accent")

                ctx.beginPath()
                ctx.moveTo(x, 0)
                ctx.lineTo(x, height)
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
        frameId = requestAnimationFrame(render)

        return () => cancelAnimationFrame(frameId)
    }, [width, height, viewport, canvasRef, tracks])
}
