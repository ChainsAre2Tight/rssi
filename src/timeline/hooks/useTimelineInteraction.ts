import { useRef } from "react"
import type { Viewport } from "../types"
import { MIN_DURATION } from "../config"

interface Params {
    viewport: Viewport
    setViewport: (v: Viewport) => void
    width: number
}

export function useTimelineInteraction({
    viewport,
    setViewport,
    width,
}: Params) {
    const isPanning = useRef(false)
    const isZooming = useRef(false)

    const dragStartX = useRef(0)
    const dragStartViewport = useRef<Viewport | null>(null)

    const zoomStartDuration = useRef(0)
    const zoomAnchorTime = useRef(0)
    const zoomAnchorX = useRef<number | null>(null)

    const cursor = useRef<{ x: number; y: number } | null>(null)

    const getDuration = () => viewport.end - viewport.start

    function getCanvasCoords(e: React.MouseEvent) {
        const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()

        const x = ((e.clientX - rect.left) / rect.width) * width
        const y = ((e.clientY - rect.top) / rect.height) * rect.height

        return { x, y }
    }

    function panByPixels(deltaPx: number) {
        const duration = getDuration()
        const scale = width / duration
        const deltaTime = deltaPx / scale

        setViewport({
            start: viewport.start - deltaTime,
            end: viewport.end - deltaTime,
        })
    }

    function zoomFromDrag(deltaPx: number) {
        if (!dragStartViewport.current) return
        if (Math.abs(deltaPx) < 2) return

        const startDuration = zoomStartDuration.current

        const zoomStrength = 0.005
        const zoomFactor = Math.exp(-deltaPx * zoomStrength)

        let newDuration = startDuration * zoomFactor
        newDuration = Math.max(newDuration, MIN_DURATION)

        const anchor = zoomAnchorTime.current

        const ratio =
            (anchor - dragStartViewport.current.start) / startDuration

        const newStart = anchor - ratio * newDuration
        const newEnd = newStart + newDuration

        setViewport({
            start: newStart,
            end: newEnd,
        })
    }

    function onMouseDown(e: React.MouseEvent) {
        const { x, y } = getCanvasCoords(e)

        dragStartX.current = e.clientX
        dragStartViewport.current = { ...viewport }

        if (e.button === 0) {
            isPanning.current = true
        }

        if (e.button === 2) {
            isZooming.current = true

            const duration = getDuration()
            zoomStartDuration.current = duration

            zoomAnchorTime.current =
                viewport.start + (x / width) * duration

            zoomAnchorX.current = x
        }

        cursor.current = { x, y }
    }

    function onMouseMove(e: React.MouseEvent) {
        const { x, y } = getCanvasCoords(e)

        if (!isZooming.current) {
            cursor.current = { x, y }
        }

        if (!dragStartViewport.current) return

        const deltaPx = e.clientX - dragStartX.current

        if (isPanning.current) {
            const duration =
                dragStartViewport.current.end -
                dragStartViewport.current.start

            const scale = width / duration
            const deltaTime = deltaPx / scale

            setViewport({
                start: dragStartViewport.current.start - deltaTime,
                end: dragStartViewport.current.end - deltaTime,
            })
        }

        if (isZooming.current) {
            zoomFromDrag(deltaPx)
        }
    }

    function onMouseUp() {
        isPanning.current = false
        isZooming.current = false
        zoomAnchorX.current = null
    }

    function onMouseLeave() {
        isPanning.current = false
        isZooming.current = false
        cursor.current = null
        zoomAnchorX.current = null
    }

    function onWheel(e: React.WheelEvent) {
        if (width === 0) return
        e.preventDefault()
        panByPixels(e.deltaY)
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
        zoomAnchorX,
        isZooming,
    }
}