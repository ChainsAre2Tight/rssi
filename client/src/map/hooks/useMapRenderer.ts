import { useEffect } from "react"
import type { RefObject } from "react"
import type { MapAdapterResult, SpatialViewport } from "../types"
import { worldToCanvas } from "../utils/geometry"

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

            // Clear canvas
            const bgColor = getColor("--color-bg", "#1a1a1a")
            ctx.fillStyle = bgColor
            ctx.fillRect(0, 0, width, height)

            // Draw grid
            drawGrid(ctx, width, height, viewport)

            // Draw sensors
            drawSensors(ctx, width, height, viewport, adapter)

            // Draw trajectory segments
            drawSegments(ctx, width, height, viewport, adapter)

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
    viewport: SpatialViewport
) {
    const gridColor = getColor("--color-border", "#333333")
    const textColor = getColor("--color-text-secondary", "#999999")

    ctx.strokeStyle = gridColor
    ctx.lineWidth = 1
    ctx.font = "11px monospace"
    ctx.fillStyle = textColor
    ctx.textAlign = "right"
    ctx.textBaseline = "bottom"

    // Calculate grid lines
    let gridStart = Math.floor(viewport.minX / GRID_SPACING) * GRID_SPACING
    let gridEnd = Math.ceil(viewport.maxX / GRID_SPACING) * GRID_SPACING

    // Draw vertical grid lines and X labels
    for (let x = gridStart; x <= gridEnd; x += GRID_SPACING) {
        const canvasX = ((x - viewport.minX) / (viewport.maxX - viewport.minX)) * width

        ctx.beginPath()
        ctx.moveTo(canvasX, 0)
        ctx.lineTo(canvasX, height)
        ctx.stroke()

        // X labels at bottom
        const label = `+${Math.round(x)}m`
        ctx.fillText(label, canvasX - 2, height - 2)
    }

    gridStart = Math.floor(viewport.minY / GRID_SPACING) * GRID_SPACING
    gridEnd = Math.ceil(viewport.maxY / GRID_SPACING) * GRID_SPACING

    ctx.textAlign = "left"
    ctx.textBaseline = "middle"

    // Draw horizontal grid lines and Y labels
    for (let y = gridStart; y <= gridEnd; y += GRID_SPACING) {
        const canvasY = height - ((y - viewport.minY) / (viewport.maxY - viewport.minY)) * height

        ctx.beginPath()
        ctx.moveTo(0, canvasY)
        ctx.lineTo(width, canvasY)
        ctx.stroke()

        // Y labels at left
        const label = `+${Math.round(y)}m`
        ctx.fillText(label, 2, canvasY)
    }
}

function drawSensors(
    ctx: CanvasRenderingContext2D,
    width: number,
    height: number,
    viewport: SpatialViewport,
    adapter: MapAdapterResult
) {
    const dotRadius = 4
    const sensorColor = getColor("--color-accent", "#4a90e2")
    const labelColor = getColor("--color-text-secondary", "#999999")

    ctx.fillStyle = sensorColor
    ctx.strokeStyle = "white"
    ctx.lineWidth = 2

    for (const sensor of adapter.sensors) {
        const canvasCoords = worldToCanvas(sensor.x, sensor.y, viewport, width, height)

        // Draw dot
        ctx.beginPath()
        ctx.arc(canvasCoords.x, canvasCoords.y, dotRadius, 0, Math.PI * 2)
        ctx.fill()
        ctx.stroke()

        // Draw label
        ctx.fillStyle = labelColor
        ctx.font = "11px sans-serif"
        ctx.textAlign = "left"
        ctx.textBaseline = "top"
        ctx.fillText(sensor.name, canvasCoords.x + 6, canvasCoords.y - 6)
    }
}

function drawSegments(
    ctx: CanvasRenderingContext2D,
    width: number,
    height: number,
    viewport: SpatialViewport,
    adapter: MapAdapterResult
) {
    const textColor = getColor("--color-text", "#cccccc")

    for (const segment of adapter.segments) {
        if (segment.points.length < 1) continue

        // Set line style based on calibration and gap type
        ctx.strokeStyle = textColor
        ctx.lineWidth = segment.style.calibrated ? 2 : 1
        ctx.globalAlpha = segment.style.calibrated ? 1 : 0.6

        if (segment.style.gapType === "dashed") {
            ctx.setLineDash([4, 4])
        } else {
            ctx.setLineDash([])
        }

        // Draw path
        ctx.beginPath()

        const firstCanvasCoords = worldToCanvas(
            segment.points[0].x,
            segment.points[0].y,
            viewport,
            width,
            height
        )
        ctx.moveTo(firstCanvasCoords.x, firstCanvasCoords.y)

        for (let i = 1; i < segment.points.length; i++) {
            const canvasCoords = worldToCanvas(
                segment.points[i].x,
                segment.points[i].y,
                viewport,
                width,
                height
            )
            ctx.lineTo(canvasCoords.x, canvasCoords.y)
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

