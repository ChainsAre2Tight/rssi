import { useEffect } from "react"
import type { RefObject } from "react"
import type { TimelineAdapterResult, TimelineItem, TrackLayoutItem, Viewport } from "../types"
import { createTimeMapper } from "../utils/mapping"
import { RESIZE_HANDLE_GAP } from "../config"
import { getSeverityColor } from "../../utils/severity"
import { formatDateTime } from "../../utils/time"

function adjustBrightness(color: string, brightness: number): string {
    let r: number, g: number, b: number

    // Parse hex color
    if (color.startsWith("#")) {
        const hex = color.slice(1)
        r = parseInt(hex.slice(0, 2), 16)
        g = parseInt(hex.slice(2, 4), 16)
        b = parseInt(hex.slice(4, 6), 16)
    }
    // Parse rgb color
    else if (color.startsWith("rgb")) {
        const match = color.match(/\d+/g)
        if (!match || match.length < 3) return color
        r = parseInt(match[0])
        g = parseInt(match[1])
        b = parseInt(match[2])
    } else {
        return color
    }

    // Apply brightness
    r = Math.round(Math.min(255, r * brightness))
    g = Math.round(Math.min(255, g * brightness))
    b = Math.round(Math.min(255, b * brightness))

    return `rgb(${r},${g},${b})`
}

interface Params {
    canvasRef: RefObject<HTMLCanvasElement>
    width: number
    height: number
    viewport: Viewport
    cursor: RefObject<{ x: number; y: number } | null>
    zoomAnchorX: RefObject<number | null>
    isZooming: RefObject<boolean>
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

            function getStep(raw: number) {
                const pow = Math.pow(10, Math.floor(Math.log10(raw)))
                const norm = raw / pow

                let step
                if (norm <= 1) step = 1
                else if (norm <= 2) step = 2
                else if (norm <= 5) step = 5
                else step = 10

                return step * pow
            }

            const majorStep = getStep(targetPxPerTick / scale)
            const minorStep = majorStep / 5

            const firstMajor = Math.floor(viewport.start / majorStep) * majorStep
            const firstMinor = Math.floor(viewport.start / minorStep) * minorStep

            // styles
            ctx.lineWidth = 1

            const gridColor = styles.getPropertyValue("--color-border")
            const textColor = styles.getPropertyValue("--color-text-muted") || "#888"

            // --- MINOR GRID ---
            ctx.strokeStyle = gridColor
            ctx.globalAlpha = 0.2

            let minorCount = 0
            for (let t = firstMinor; t < viewport.end; t += minorStep) {
                const x = Math.round((t - viewport.start) * scale) + 0.5

                ctx.beginPath()
                ctx.moveTo(x, 0)
                ctx.lineTo(x, height)
                ctx.stroke()

                if (++minorCount > 300) break // safety cap
            }

            ctx.globalAlpha = 1

            // --- MAJOR GRID + LABELS ---
            const GRID_LABEL_Y = height - 4
            const BOUNDS_LABEL_Y = height - 18

            ctx.strokeStyle = gridColor
            ctx.globalAlpha = 0.6

            ctx.font = "11px sans-serif"
            ctx.fillStyle = textColor
            ctx.textBaseline = "bottom"

            let lastLabelX = -Infinity

            function formatTime(seconds: number) {
                const d = new Date(seconds * 1000)

                const year = d.getFullYear()
                const month = d.toLocaleString("default", { month: "short" })
                const day = d.getDate().toString().padStart(2, "0")

                const hh = d.getHours().toString().padStart(2, "0")
                const mm = d.getMinutes().toString().padStart(2, "0")
                const ss = d.getSeconds().toString().padStart(2, "0")

                if (majorStep < 60) {
                    return `${hh}:${mm}:${ss}`
                }

                if (majorStep < 3600) {
                    return `${day} ${hh}:${mm}`
                }

                if (majorStep < 86400) {
                    return `${month} ${day} ${hh}:00`
                }

                if (majorStep < 86400 * 30) {
                    return `${month} ${day}`
                }

                return `${year} ${month}`
            }

            let majorCount = 0

            for (let t = firstMajor; t < viewport.end; t += majorStep) {
                const x = Math.round((t - viewport.start) * scale) + 0.5

                // line
                ctx.beginPath()
                ctx.moveTo(x, 0)
                ctx.lineTo(x, height)
                ctx.stroke()

                // label (collision safe)
                if (x - lastLabelX > 60) {
                    const label = formatTime(t)
                    ctx.fillText(label, x + 4, GRID_LABEL_Y)
                    lastLabelX = x
                }

                if (++majorCount > 200) break // safety cap
            }

            ctx.globalAlpha = 1

            // --- INITIAL BOUNDS MARKERS ---
            const boundsStartS = adapter.bounds.start / 1_000_000
            const boundsEndS = adapter.bounds.end / 1_000_000

            const xStart = mapper.toX(boundsStartS)
            const xEnd = mapper.toX(boundsEndS)

            ctx.save()

            ctx.strokeStyle = styles.getPropertyValue("--color-accent")
            ctx.lineWidth = 2
            ctx.globalAlpha = 0.6
            ctx.setLineDash([6, 4])

            // vertical lines
            ctx.beginPath()
            ctx.moveTo(xStart, 0)
            ctx.lineTo(xStart, height)
            ctx.moveTo(xEnd, 0)
            ctx.lineTo(xEnd, height)
            ctx.stroke()

            ctx.setLineDash([])
            ctx.globalAlpha = 1

            // --- LABELS (BOTTOM, ABOVE GRID LABELS) ---
            ctx.font = "11px sans-serif"
            ctx.fillStyle = styles.getPropertyValue("--color-accent")
            ctx.textBaseline = "bottom"

            const startLabel = formatDateTime(adapter.bounds.start)
            const endLabel = formatDateTime(adapter.bounds.end)

            // clamp helper
            function clampX(x: number, textWidth: number) {
                return Math.max(4, Math.min(width - textWidth - 4, x))
            }

            // START label
            if (xStart >= -50 && xStart <= width + 50) {
                const w = ctx.measureText(startLabel).width
                const x = clampX(xStart + 4, w)
                ctx.fillText(startLabel, x, BOUNDS_LABEL_Y)
            }

            // END label
            if (xEnd >= -50 && xEnd <= width + 50) {
                const w = ctx.measureText(endLabel).width
                const x = clampX(xEnd - w - 4, w)
                ctx.fillText(endLabel, x, BOUNDS_LABEL_Y)
            }

            ctx.restore()


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

                        let color = getSeverityColor(item.severity, styles)

                        // Apply brightness based on interaction state
                        if (item === hoveredItem) {
                            color = adjustBrightness(color, 1.2)
                        } else if (item === selectedItem) {
                            color = adjustBrightness(color, 1.15)
                        } else {
                            color = adjustBrightness(color, 0.8)
                        }

                        ctx.fillStyle = color
                        ctx.beginPath()
                        ctx.roundRect(x, y, Math.max(w, 4), h, 4)
                        ctx.fill()                     
                    }
                }

                ctx.restore()
            }

            ctx.setLineDash([])

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
