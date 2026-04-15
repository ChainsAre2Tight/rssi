import { useRef } from "react"
import type { SpatialViewport } from "../types"
import type { SpatialMapper } from "../utils/spatialMapper"

const MIN_WORLD_SIZE = 1      // 1 meter (max zoom-in)
const MAX_WORLD_SIZE = 100    // 100 meters (max zoom-out)

interface Params {
    viewport: SpatialViewport
    setViewport: (v: SpatialViewport) => void
    canvasWidth: number
    canvasHeight: number
    mapper: SpatialMapper
    onClick?: (x: number, y: number) => void
    onMove?: (x: number, y: number) => void
}

export function useMapInteraction({
    viewport,
    setViewport,
    canvasWidth,
    canvasHeight,
    mapper,
    onClick,
    onMove,
}: Params) {

    function safeSetViewport(next: SpatialViewport) {
        if (
            !Number.isFinite(next.minX) ||
            !Number.isFinite(next.maxX) ||
            !Number.isFinite(next.minY) ||
            !Number.isFinite(next.maxY)
        ) {
            return
        }

        if (next.maxX - next.minX <= 0 || next.maxY - next.minY <= 0) {
            return
        }

        setViewport(next)
    }

    const isPanning = useRef(false)

    const dragStartClientX = useRef(0)
    const dragStartClientY = useRef(0)
    const dragStartViewport = useRef<SpatialViewport | null>(null)
    const didDrag = useRef(false)

    const cursor = useRef<{ x: number; y: number, world: {x: number; y: number} } | null>(null)

    function getCanvasCoords(e: React.MouseEvent) {
        const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()

        const x = e.clientX - rect.left
        const y = e.clientY - rect.top

        return { x, y }
    }

    function panFromStart(deltaPxX: number, deltaPxY: number) {
        if (!dragStartViewport.current) return

        const base = dragStartViewport.current

        const deltaWorldX = deltaPxX / mapper.scale
        const deltaWorldY = deltaPxY / mapper.scale

        safeSetViewport({
            minX: base.minX - deltaWorldX,
            maxX: base.maxX - deltaWorldX,
            minY: base.minY + deltaWorldY,
            maxY: base.maxY + deltaWorldY,
        })
    }

    function zoomAtPoint(canvasX: number, canvasY: number, zoomFactor: number) {
        const anchor = mapper.toWorld(canvasX, canvasY)

        const width = viewport.maxX - viewport.minX
        const height = viewport.maxY - viewport.minY

        let newWidth = width * zoomFactor
        let newHeight = height * zoomFactor

        const relX = (anchor.x - viewport.minX) / width
        const relY = (anchor.y - viewport.minY) / height

        let minX = anchor.x - newWidth * relX
        let maxX = anchor.x + newWidth * (1 - relX)

        let minY = anchor.y - newHeight * relY
        let maxY = anchor.y + newHeight * (1 - relY)

        const clamped = clampViewportSize(
            minX,
            maxX,
            minY,
            maxY,
            anchor.x,
            anchor.y
        )

        safeSetViewport(clamped)
    }

    function onMouseDown(e: React.MouseEvent) {
        const { x, y } = getCanvasCoords(e)

        dragStartClientX.current = e.clientX
        dragStartClientY.current = e.clientY
        dragStartViewport.current = { ...viewport }
        didDrag.current = false

        if (e.button === 0) {
            isPanning.current = true
        }

        const world = mapper.toWorld(x, y)
        cursor.current = { x, y, world }
    }

    function onMouseMove(e: React.MouseEvent) {
        const { x, y } = getCanvasCoords(e)

        // Always update cursor position for hover feedback
        const world = mapper.toWorld(x, y)
        cursor.current = { x, y, world }

        onMove?.(x, y)

        if (!dragStartViewport.current) return

        const deltaPxX = e.clientX - dragStartClientX.current
        const deltaPxY = e.clientY - dragStartClientY.current

        if (!didDrag.current && Math.abs(deltaPxX) > 5) {
            didDrag.current = true
        }

        if (isPanning.current && didDrag.current) {
            panFromStart(deltaPxX, deltaPxY)
        }
    }

    function onMouseUp(e: React.MouseEvent) {
        if (!didDrag.current) {
            const { x, y } = getCanvasCoords(e)
            onClick?.(x, y)
        }

        isPanning.current = false
    }

    function onMouseLeave() {
        isPanning.current = false
        cursor.current = null
    }

    function onWheel(e: React.WheelEvent) {
        if (canvasWidth === 0 || canvasHeight === 0) return

        e.preventDefault()

        const { x, y } = getCanvasCoords(e)

        const zoomStrength = 0.0015
        const zoomFactor = Math.exp(e.deltaY * zoomStrength)

        zoomAtPoint(x, y, zoomFactor)
    }

    function onContextMenu(e: React.MouseEvent) {
        e.preventDefault()
    }

    return {
        bind: {
            onWheel,
            onMouseDown,
            onMouseMove,
            onMouseUp,
            onMouseLeave,
            onContextMenu,
        },
        cursor,
    }
}

function clampViewportSize(
    minX: number,
    maxX: number,
    minY: number,
    maxY: number,
    anchorX: number,
    anchorY: number
) {
    let width = maxX - minX
    let height = maxY - minY

    // Clamp sizes
    const clampedWidth = Math.min(Math.max(width, MIN_WORLD_SIZE), MAX_WORLD_SIZE)
    const clampedHeight = Math.min(Math.max(height, MIN_WORLD_SIZE), MAX_WORLD_SIZE)

    // If no clamp → return original (important: prevents drift)
    if (clampedWidth === width && clampedHeight === height) {
        return { minX, maxX, minY, maxY }
    }

    // Preserve anchor position
    const relX = (anchorX - minX) / width
    const relY = (anchorY - minY) / height

    const newMinX = anchorX - clampedWidth * relX
    const newMaxX = anchorX + clampedWidth * (1 - relX)

    const newMinY = anchorY - clampedHeight * relY
    const newMaxY = anchorY + clampedHeight * (1 - relY)

    return {
        minX: newMinX,
        maxX: newMaxX,
        minY: newMinY,
        maxY: newMaxY,
    }
}
