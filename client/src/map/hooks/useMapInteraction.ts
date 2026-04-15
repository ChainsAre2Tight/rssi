import { useRef } from "react"
import type { SpatialViewport } from "../types"
import { zoomViewport, panViewport, canvasToWorld } from "../utils/geometry"

interface Params {
    viewport: SpatialViewport
    setViewport: (v: SpatialViewport) => void
    canvasWidth: number
    canvasHeight: number
    onClick?: (x: number, y: number) => void
    onMove?: (x: number, y: number) => void
}

export function useMapInteraction({
    viewport,
    setViewport,
    canvasWidth,
    canvasHeight,
    onClick,
    onMove,
}: Params) {
    const isPanning = useRef(false)
    const isZooming = useRef(false)

    const dragStartX = useRef(0)
    const dragStartY = useRef(0)
    const dragStartViewport = useRef<SpatialViewport | null>(null)
    const didDrag = useRef(false)

    const zoomAnchorX = useRef<number | null>(null)
    const zoomAnchorY = useRef<number | null>(null)

    const cursor = useRef<{ x: number; y: number } | null>(null)

    function getCanvasCoords(e: React.MouseEvent) {
        const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()

        const x = e.clientX - rect.left
        const y = e.clientY - rect.top

        return { x, y }
    }

    function panByPixels(deltaPxX: number, deltaPxY: number) {
        const width = viewport.maxX - viewport.minX
        const height = viewport.maxY - viewport.minY

        const scaleX = width / canvasWidth
        const scaleY = height / canvasHeight

        const deltaWorldX = deltaPxX * scaleX
        const deltaWorldY = deltaPxY * scaleY

        setViewport(panViewport(viewport, deltaWorldX, -deltaWorldY))
    }

    function zoomFromDrag(deltaPx: number) {
        if (!dragStartViewport.current) return
        if (Math.abs(deltaPx) < 2) return

        const zoomStrength = 0.005
        const zoomFactor = Math.exp(-deltaPx * zoomStrength)

        const anchorX =
            zoomAnchorX.current !== null
                ? viewport.minX + (zoomAnchorX.current / canvasWidth) * (viewport.maxX - viewport.minX)
                : undefined

        const anchorY =
            zoomAnchorY.current !== null
                ? viewport.maxY - (zoomAnchorY.current / canvasHeight) * (viewport.maxY - viewport.minY)
                : undefined

        const next = zoomViewport(
            dragStartViewport.current,
            zoomFactor,
            anchorX,
            anchorY
        )

        setViewport(next)
    }

    function onMouseDown(e: React.MouseEvent) {
        const { x, y } = getCanvasCoords(e)

        dragStartX.current = x
        dragStartY.current = y
        dragStartViewport.current = { ...viewport }
        didDrag.current = false

        if (e.button === 0) {
            isPanning.current = true
        }

        if (e.button === 2) {
            isZooming.current = true
            zoomAnchorX.current = x
            zoomAnchorY.current = y
        }

        cursor.current = { x, y }
    }

    function onMouseMove(e: React.MouseEvent) {
        const { x, y } = getCanvasCoords(e)

        cursor.current = { x, y }
        onMove?.(x, y)

        if (!dragStartViewport.current) return

        const deltaPxX = x - dragStartX.current
        const deltaPxY = y - dragStartY.current

        if (!didDrag.current && Math.abs(deltaPxX) > 5) {
            didDrag.current = true
        }

        if (isPanning.current && didDrag.current) {
            panByPixels(deltaPxX, deltaPxY)
        }

        if (isZooming.current) {
            zoomFromDrag(deltaPxY)
        }
    }

    function onMouseUp(e: React.MouseEvent) {
        if (!didDrag.current && !isZooming.current) {
            const { x, y } = getCanvasCoords(e)
            onClick?.(x, y)
        }

        isPanning.current = false
        isZooming.current = false
        zoomAnchorX.current = null
        zoomAnchorY.current = null
    }

    function onMouseLeave() {
        isPanning.current = false
        isZooming.current = false
        cursor.current = null
        zoomAnchorX.current = null
        zoomAnchorY.current = null
    }

    function onWheel(e: React.WheelEvent) {
        if (canvasWidth === 0 || canvasHeight === 0) return
        e.preventDefault()
        panByPixels(0, e.deltaY)
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
