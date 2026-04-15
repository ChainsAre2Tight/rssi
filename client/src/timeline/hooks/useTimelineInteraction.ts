import { useRef } from "react"
import type { TimelineTrack, TrackLayoutItem, Viewport } from "../types"
import { zoomViewport } from "../utils/zoomViewport"
import { findTrackAtY } from "../utils/mapping"

interface Params {
    viewport: Viewport
    setViewport: (v: Viewport) => void
    width: number
    onClick?: (x: number, y: number) => void
    onMove?: (x: number, y: number) => void
    layout: TrackLayoutItem[]
    tracks: TimelineTrack[]
    setTracks: React.Dispatch<React.SetStateAction<TimelineTrack[]>>
}

export function useTimelineInteraction({
    viewport,
    setViewport,
    width,
    onClick,
    onMove,
    layout,
    tracks,
    setTracks,
}: Params) {
    const isPanning = useRef(false)
    const isZooming = useRef(false)

    const dragStartX = useRef(0)
    const dragStartViewport = useRef<Viewport | null>(null)
    const didDrag = useRef(false)

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

        const zoomStrength = 0.005
        const zoomFactor = Math.exp(-deltaPx * zoomStrength)

        const next = zoomViewport({
            viewport: dragStartViewport.current,
            zoomFactor,
            anchorTime: zoomAnchorTime.current,
        })

        setViewport(next)
    }

    function onMouseDown(e: React.MouseEvent) {
        const { x, y } = getCanvasCoords(e)

        dragStartX.current = e.clientX
        dragStartViewport.current = { ...viewport }
        didDrag.current = false

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
            onMove?.(x, y)
        }

        if (!dragStartViewport.current) return

        const deltaPx = e.clientX - dragStartX.current

        if (!didDrag.current && Math.abs(deltaPx) > 5) {
            didDrag.current = true
        }

        if (isPanning.current && didDrag.current) {
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

    function onMouseUp(e: React.MouseEvent) {
        if (!didDrag.current && !isZooming.current) {
            const { x, y } = getCanvasCoords(e)
            onClick?.(x, y)
        }

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

        const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
        const y = e.clientY - rect.top

        if (e.shiftKey) {
            const trackLayout = findTrackAtY(y, layout)
            if (!trackLayout) return

            const trackId = trackLayout.id

            setTracks(prev =>
                prev.map(t => {
                    if (t.id !== trackId) return t

                    const scrollY = t.scrollY ?? 0

                    const maxScroll = Math.max(
                        0,
                        trackLayout.contentHeight - trackLayout.viewportHeight
                    )

                    const nextScroll = Math.min(
                        maxScroll,
                        Math.max(0, scrollY + e.deltaY)
                    )

                    return {
                        ...t,
                        scrollY: nextScroll,
                    }
                })
            )

            return
        }

        // default behavior (horizontal pan)
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
