import { useRef } from "react"
import type { SpatialViewport } from "../types"
import { zoomViewport } from "../utils/geometry"
import type { SpatialMapper } from "../utils/spatialMapper"

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
    const isPanning = useRef(false)

    const dragStartClientX = useRef(0)
    const dragStartClientY = useRef(0)
    const dragStartViewport = useRef<SpatialViewport | null>(null)
    const didDrag = useRef(false)

    const zoomAnchorX = useRef<number | null>(null)
    const zoomAnchorY = useRef<number | null>(null)

    const cursor = useRef<{ x: number; y: number, world: {x: number; y: number} } | null>(null)

    function getCanvasCoords(e: React.MouseEvent) {
        const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()

        const x = e.clientX - rect.left
        const y = e.clientY - rect.top

        return { x, y }
    }

    function panByPixels(deltaPxX: number, deltaPxY: number) {
        const deltaWorldX = deltaPxX / mapper.scale
        const deltaWorldY = deltaPxY / mapper.scale

        setViewport({
            minX: viewport.minX - deltaWorldX,
            maxX: viewport.maxX - deltaWorldX,
            minY: viewport.minY + deltaWorldY,
            maxY: viewport.maxY + deltaWorldY,
        })
    }

    function zoomAtPoint(canvasX: number, canvasY: number, zoomFactor: number) {
        const anchor = mapper.toWorld(canvasX, canvasY)

        const width = viewport.maxX - viewport.minX
        const height = viewport.maxY - viewport.minY

        const newWidth = width * zoomFactor
        const newHeight = height * zoomFactor

        const relX = (anchor.x - viewport.minX) / width
        const relY = (anchor.y - viewport.minY) / height

        const minX = anchor.x - newWidth * relX
        const maxX = anchor.x + newWidth * (1 - relX)

        const minY = anchor.y - newHeight * relY
        const maxY = anchor.y + newHeight * (1 - relY)

        setViewport({ minX, maxX, minY, maxY })
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
            panByPixels(deltaPxX, deltaPxY)
        }
    }

    function onMouseUp(e: React.MouseEvent) {
        if (!didDrag.current) {
            const { x, y } = getCanvasCoords(e)
            onClick?.(x, y)
        }

        isPanning.current = false
        zoomAnchorX.current = null
        zoomAnchorY.current = null
    }

    function onMouseLeave() {
        isPanning.current = false
        cursor.current = null
        zoomAnchorX.current = null
        zoomAnchorY.current = null
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
