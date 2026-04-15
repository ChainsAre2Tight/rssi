import { useEffect } from "react"
import type { RefObject } from "react"
import type { MapAdapterResult, SpatialViewport } from "../types"
import { createSpatialMapper, type SpatialMapper } from "../utils/spatialMapper"


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

function drawAxisGrid({
    ctx,
    mapper,
    isVertical,
    start,
    end,
    majorStep,
    minorStep,
    length,
    gridColor,
    textColor,
    width,
    height,
}: any) {
    ctx.lineWidth = 1

    const firstMajor = Math.floor(start / majorStep) * majorStep
    const firstMinor = Math.floor(start / minorStep) * minorStep

    // --- MINOR ---
    ctx.strokeStyle = gridColor
    ctx.globalAlpha = 0.2

    for (let v = firstMinor; v < end; v += minorStep) {
        const p = isVertical
            ? mapper.toCanvas(v, 0)
            : mapper.toCanvas(0, v)

        const pos = isVertical ? p.x : p.y

        ctx.beginPath()
        if (isVertical) {
            ctx.moveTo(pos, 0)
            ctx.lineTo(pos, height)
        } else {
            ctx.moveTo(0, pos)
            ctx.lineTo(width, pos)
        }
        ctx.stroke()
    }

    // --- MAJOR ---
    ctx.globalAlpha = 0.6
    ctx.strokeStyle = gridColor
    ctx.fillStyle = textColor
    ctx.font = "11px monospace"

    let lastLabelPos = -Infinity

    for (let v = firstMajor; v < end; v += majorStep) {
        const p = isVertical
            ? mapper.toCanvas(v, 0)
            : mapper.toCanvas(0, v)

        const pos = isVertical ? p.x : p.y

        ctx.beginPath()
        if (isVertical) {
            ctx.moveTo(pos, 0)
            ctx.lineTo(pos, height)
        } else {
            ctx.moveTo(0, pos)
            ctx.lineTo(width, pos)
        }
        ctx.stroke()

        // label spacing control
        if (Math.abs(pos - lastLabelPos) > 60) {
            const label = `${v.toFixed(1)}m`

            if (isVertical) {
                ctx.textAlign = "left"
                ctx.textBaseline = "bottom"
                ctx.fillText(label, pos + 4, height - 4)
            } else {
                console.log(pos)
                ctx.textAlign = "left"
                ctx.textBaseline = "middle"
                ctx.fillText(label, 4, pos)
            }

            lastLabelPos = pos
        }
    }

    ctx.globalAlpha = 1
}

function getExtendedWorldBounds(
    mapper: SpatialMapper,
    width: number,
    height: number
) {
    const left = mapper.toWorld(0, 0).x
    const right = mapper.toWorld(width, 0).x

    const bottom = mapper.toWorld(0, height).y
    const top = mapper.toWorld(0, 0).y

    return {
        minX: Math.min(left, right),
        maxX: Math.max(left, right),
        minY: Math.min(bottom, top),
        maxY: Math.max(bottom, top),
    }
}

function drawGrid(
    ctx: CanvasRenderingContext2D,
    width: number,
    height: number,
    viewport: SpatialViewport,
    mapper: SpatialMapper
) {
    const gridColor = getColor("--color-border", "#333")
    const textColor = getColor("--color-text-secondary", "#999")

    const worldWidth = viewport.maxX - viewport.minX
    const pxPerUnit = width / worldWidth

    const targetPx = 200 // desired spacing for MAJOR lines
    const extended = getExtendedWorldBounds(mapper, width, height)

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

    const majorStep = getStep(targetPx / pxPerUnit)
    const minorStep = majorStep / 5

    // --- X GRID ---
    drawAxisGrid({
        ctx,
        mapper,
        isVertical: true,
        start: extended.minX,
        end: extended.maxX,
        majorStep,
        minorStep,
        length: height,
        gridColor,
        textColor,
        width,
        height,
    })

    // --- Y GRID ---
    drawAxisGrid({
        ctx,
        mapper,
        isVertical: false,
        start: extended.minY,
        end: extended.maxY,
        majorStep,
        minorStep,
        length: width,
        gridColor,
        textColor,
        width,
        height,
    })
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

