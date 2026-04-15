import { useEffect } from "react"
import type { RefObject } from "react"
import type { MapAdapterResult, SpatialViewport } from "../types"
import { worldToCanvas } from "../utils/geometry"
import { createSpatialMapper, type SpatialMapper } from "../utils/spatialMapper"

const GRID_SPACING = 1.0 // 1 meter

interface Params {
    canvasRef: RefObject<HTMLCanvasElement>
    width: number
    height: number
    viewport: SpatialViewport
    adapter: MapAdapterResult
    cursor: RefObject<{ x: number; y: number } | null>
}

function getColor(varName: string, fallback: string): string {
    try {
        const color = getComputedStyle(document.documentElement).getPropertyValue(varName).trim()
        return color || fallback
    } catch {
        return fallback
    }
}

export function useMapRenderer({
    canvasRef,
    width,
    height,
    viewport,
    adapter,
    cursor,
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

            const mapper = createSpatialMapper(viewport, width, height)

            // Clear canvas
            const bgColor = getColor("--color-bg", "#1a1a1a")
            ctx.fillStyle = bgColor
            ctx.fillRect(0, 0, width, height)

            // Draw grid
            drawGrid(ctx, width, height, viewport, mapper)

            // Draw sensors
            drawSensors(ctx, mapper, adapter)

            // Draw trajectory segments
            drawSegments(ctx, mapper, adapter)

            // Draw crosshair cursor
            if (cursor.current) {
                drawCrosshair(ctx, cursor.current.x, cursor.current.y, width, height)
            }

            frameId = requestAnimationFrame(render)
        }

        frameId = requestAnimationFrame(render)

        return () => {
            if (frameId) {
                cancelAnimationFrame(frameId)
            }
        }
    }, [canvasRef, width, height, viewport, adapter, cursor])
}

function drawGrid(
    ctx: CanvasRenderingContext2D,
    width: number,
    height: number,
    viewport: SpatialViewport,
    mapper: ReturnType<typeof createSpatialMapper>
) {
    const gridColor = getColor("--color-border", "#333333")
    const textColor = getColor("--color-text-secondary", "#999999")

    ctx.strokeStyle = gridColor
    ctx.lineWidth = 1
    ctx.font = "11px monospace"
    ctx.fillStyle = textColor

    const GRID_SPACING = 1

    let xStart = Math.floor(viewport.minX)
    let xEnd = Math.ceil(viewport.maxX)

    for (let x = xStart; x <= xEnd; x += GRID_SPACING) {
        const p = mapper.toCanvas(x, viewport.minY)

        ctx.beginPath()
        ctx.moveTo(p.x, 0)
        ctx.lineTo(p.x, height)
        ctx.stroke()

        ctx.fillText(`+${x}m`, p.x - 2, height - 2)
    }

    let yStart = Math.floor(viewport.minY)
    let yEnd = Math.ceil(viewport.maxY)

    for (let y = yStart; y <= yEnd; y += GRID_SPACING) {
        const p = mapper.toCanvas(viewport.minX, y)

        ctx.beginPath()
        ctx.moveTo(0, p.y)
        ctx.lineTo(width, p.y)
        ctx.stroke()

        ctx.fillText(`+${y}m`, 2, p.y)
    }
}

function drawSensors(
    ctx: CanvasRenderingContext2D,
    mapper: ReturnType<typeof createSpatialMapper>,
    adapter: MapAdapterResult
) {
    const dotRadius = 4
    const sensorColor = getColor("--color-accent", "#4a90e2")
    const labelColor = getColor("--color-text-secondary", "#999999")

    ctx.fillStyle = sensorColor
    ctx.strokeStyle = "white"
    ctx.lineWidth = 2

    for (const sensor of adapter.sensors) {
        const canvasCoords = mapper.toCanvas(sensor.x, sensor.y)

        ctx.beginPath()
        ctx.arc(canvasCoords.x, canvasCoords.y, dotRadius, 0, Math.PI * 2)
        ctx.fill()
        ctx.stroke()

        ctx.fillStyle = labelColor
        ctx.font = "11px sans-serif"
        ctx.textAlign = "left"
        ctx.textBaseline = "top"
        ctx.fillText(sensor.name, canvasCoords.x + 6, canvasCoords.y - 6)
    }
}

function drawSegments(
    ctx: CanvasRenderingContext2D,
    mapper: ReturnType<typeof createSpatialMapper>,
    adapter: MapAdapterResult
) {
    const textColor = getColor("--color-text", "#cccccc")

    for (const segment of adapter.segments) {
        if (segment.points.length < 1) continue

        ctx.strokeStyle = textColor
        ctx.lineWidth = segment.style.calibrated ? 2 : 1
        ctx.globalAlpha = segment.style.calibrated ? 1 : 0.6

        if (segment.style.gapType === "dashed") {
            ctx.setLineDash([4, 4])
        } else {
            ctx.setLineDash([])
        }

        ctx.beginPath()

        const first = mapper.toCanvas(
            segment.points[0].x,
            segment.points[0].y
        )
        ctx.moveTo(first.x, first.y)

        for (let i = 1; i < segment.points.length; i++) {
            const p = mapper.toCanvas(
                segment.points[i].x,
                segment.points[i].y
            )
            ctx.lineTo(p.x, p.y)
        }

        ctx.stroke()
    }

    ctx.setLineDash([])
    ctx.globalAlpha = 1
}

function drawCrosshair(
    ctx: CanvasRenderingContext2D,
    cursorX: number,
    cursorY: number,
    width: number,
    height: number
) {
    const crosshairColor = getColor("--color-accent", "#4a90e2")
    ctx.strokeStyle = crosshairColor
    ctx.lineWidth = 1
    ctx.globalAlpha = 0.5
    ctx.setLineDash([4, 4])

    // Horizontal line (left to right)
    ctx.beginPath()
    ctx.moveTo(0, cursorY)
    ctx.lineTo(width, cursorY)
    ctx.stroke()

    // Vertical line (top to bottom)
    ctx.beginPath()
    ctx.moveTo(cursorX, 0)
    ctx.lineTo(cursorX, height)
    ctx.stroke()

    ctx.setLineDash([])
    ctx.globalAlpha = 1
}

