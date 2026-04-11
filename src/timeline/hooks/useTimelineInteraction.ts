import { useRef } from "react"

interface Viewport {
    start: number
    end: number
}

interface Params {
    viewport: Viewport
    setViewport: (v: Viewport) => void
    width: number
}

const MIN_DURATION = 60

export function useTimelineInteraction({
    viewport,
    setViewport,
    width,
}: Params) {
    const isPanning = useRef(false)
    const isZooming = useRef(false)

    const dragStartX = useRef(0)
    const dragStartViewport = useRef<Viewport | null>(null)

    const cursorX = useRef<number | null>(null)

    const getDuration = () => viewport.end - viewport.start

    function panByPixels(deltaPx: number) {
        const duration = getDuration()
        const scale = width / duration

        const deltaTime = deltaPx / scale

        setViewport({
            start: viewport.start - deltaTime,
            end: viewport.end - deltaTime,
        })
    }

    function zoomByPixels(deltaPx: number, mouseX: number) {
        const duration = getDuration()

        const zoomStrength = 0.005
        const zoomFactor = Math.exp(-deltaPx * zoomStrength)

        let newDuration = duration * zoomFactor
        newDuration = Math.max(newDuration, MIN_DURATION)

        const ratio = mouseX / width
        const timeAtCursor =
            viewport.start + ratio * duration

        const newStart =
            timeAtCursor - ratio * newDuration

        const newEnd = newStart + newDuration

        setViewport({
            start: newStart,
            end: newEnd,
        })
    }

    function onMouseDown(e: React.MouseEvent) {
        const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
        const x = e.clientX - rect.left

        dragStartX.current = e.clientX
        dragStartViewport.current = { ...viewport }

        if (e.button === 0) {
            isPanning.current = true
        } else if (e.button === 2) {
            isZooming.current = true
        }

        cursorX.current = x
    }

    function onMouseMove(e: React.MouseEvent) {
        const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
        const x = e.clientX - rect.left
        cursorX.current = x

        if (!dragStartViewport.current) return

        const deltaPx = e.clientX - dragStartX.current

        if (isPanning.current) {
            const duration = dragStartViewport.current.end - dragStartViewport.current.start
            const scale = width / duration

            const deltaTime = deltaPx / scale

            setViewport({
                start: dragStartViewport.current.start - deltaTime,
                end: dragStartViewport.current.end - deltaTime,
            })
        }

        if (isZooming.current) {
            zoomByPixels(deltaPx, x)
        }
    }

    function onMouseUp() {
        isPanning.current = false
        isZooming.current = false
    }

    function onMouseLeave() {
        isPanning.current = false
        isZooming.current = false
        cursorX.current = null
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
        cursorX,
    }
}