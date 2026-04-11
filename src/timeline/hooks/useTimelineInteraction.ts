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

const MIN_DURATION = 60 // 1 minute

export function useTimelineInteraction({
    viewport,
    setViewport,
    width,
}: Params) {
    const dragging = useRef(false)
    const dragStartX = useRef(0)
    const dragStartViewport = useRef<Viewport | null>(null)

    const cursorX = useRef<number | null>(null)

    const getDuration = () => viewport.end - viewport.start

    // --- ZOOM ---
    function handleZoom(deltaY: number, mouseX: number) {
        const duration = getDuration()

        const zoomFactor = Math.exp(deltaY * 0.001)

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

    // --- PAN (wheel) ---
    function handlePan(deltaY: number) {
        const duration = getDuration()
        const scale = width / duration

        const deltaTime = deltaY / scale

        setViewport({
            start: viewport.start + deltaTime,
            end: viewport.end + deltaTime,
        })
    }

    // --- DRAG PAN ---
    function onMouseDown(e: React.MouseEvent) {
        dragging.current = true
        dragStartX.current = e.clientX
        dragStartViewport.current = { ...viewport }
    }

    function onMouseMove(e: React.MouseEvent) {
        const rect = (e.target as HTMLElement).getBoundingClientRect()
        const x = e.clientX - rect.left
        cursorX.current = x

        if (!dragging.current || !dragStartViewport.current) return

        const deltaPx = e.clientX - dragStartX.current
        const duration = getDuration()
        const scale = width / duration

        const deltaTime = deltaPx / scale

        setViewport({
            start: dragStartViewport.current.start - deltaTime,
            end: dragStartViewport.current.end - deltaTime,
        })
    }

    function onMouseUp() {
        dragging.current = false
    }

    function onMouseLeave() {
        dragging.current = false
        cursorX.current = null
    }

    // --- WHEEL ---
    function onWheel(e: React.WheelEvent) {
        if (width === 0) return

        if (e.ctrlKey) {
            e.preventDefault()
            handleZoom(e.deltaY, e.nativeEvent.offsetX)
        } else if (e.shiftKey) {
            e.preventDefault()
            handlePan(e.deltaY)
        }
    }

    return {
        bind: {
            onWheel,
            onMouseDown,
            onMouseMove,
            onMouseUp,
            onMouseLeave,
        },
        cursorX,
    }
}
