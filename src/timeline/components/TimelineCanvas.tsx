import { useEffect, useRef } from "react"
import { useContainerSize } from "../hooks/useContainerSize"
import { useViewport } from "../hooks/useViewport"
import { useTimelineInteraction } from "../hooks/useTimelineInteraction"
import { getNiceStep } from "../utils/timeGrid"
import styles from "./TimelineCanvas.module.css"
import { useTrackLayout } from "../hooks/useTrackLayout"
import type { TimelineTrack } from "../types"

const tracks: TimelineTrack[] = [
    { id: "track-1", height: 120, collapsible: true },
    { id: "track-2", height: 160, collapsible: true },
]

export default function TimelineCanvas() {
    const containerRef = useRef<HTMLDivElement | null>(null)
    const canvasRef = useRef<HTMLCanvasElement | null>(null)

    const { width, height } = useContainerSize(containerRef as React.RefObject<HTMLDivElement>)
    const { viewport, setViewport, duration } = useViewport()

    const { bind, cursorX, zoomAnchorX, isZooming } = useTimelineInteraction({
        viewport,
        setViewport,
        width,
    })

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

            const dpr = window.devicePixelRatio || 1

            canvas.width = width * dpr
            canvas.height = height * dpr

            ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

            // --- CLEAR ---
            ctx.fillStyle = getComputedStyle(document.documentElement)
                .getPropertyValue("--color-bg")
            ctx.fillRect(0, 0, width, height)

            // --- GRID ---
            const duration = viewport.end - viewport.start
            const scale = width / duration
            const start = viewport.start
            const end = viewport.end

            const targetPxPerTick = 100
            const rawStep = targetPxPerTick / scale
            const step = getNiceStep(rawStep)

            const firstTick = Math.floor(start / step) * step

            ctx.strokeStyle = getComputedStyle(document.documentElement)
                .getPropertyValue("--color-border")

            for (let t = firstTick; t < end; t += step) {
                const x = Math.round((t - start) * scale) + 0.5

                ctx.beginPath()
                ctx.moveTo(x, 0)
                ctx.lineTo(x, height)
                ctx.stroke()
            }

            // --- CURSOR ---
            if (isZooming.current && zoomAnchorX.current !== null) {
                const x = Math.round(zoomAnchorX.current) + 0.5

                ctx.strokeStyle = getComputedStyle(document.documentElement)
                    .getPropertyValue("--color-accent")

                ctx.lineWidth = 2

                ctx.beginPath()
                ctx.moveTo(x, 0)
                ctx.lineTo(x, height)
                ctx.stroke()
            } else if (cursorX.current !== null) {
                const x = Math.round(cursorX.current) + 0.5

                ctx.strokeStyle = getComputedStyle(document.documentElement)
                    .getPropertyValue("--color-accent")

                ctx.lineWidth = 1

                ctx.beginPath()
                ctx.moveTo(x, 0)
                ctx.lineTo(x, height)
                ctx.stroke()
            }

            frameId = requestAnimationFrame(render)
        }

        frameId = requestAnimationFrame(render)

        return () => cancelAnimationFrame(frameId)
    }, [width, height, viewport])

    // sync theme change
    // TODO: pass by tokens to render from outside
    useEffect(() => {
        const root = document.documentElement

        const observer = new MutationObserver(() => {
            // force redraw by triggering effect via size re-run
            const canvas = canvasRef.current
            if (!canvas) return

            const ctx = canvas.getContext("2d")
            if (!ctx) return

            const rect = canvas.getBoundingClientRect()

            ctx.clearRect(0, 0, rect.width, rect.height)

            ctx.fillStyle = getComputedStyle(root)
                .getPropertyValue("--color-bg")

            ctx.fillRect(0, 0, rect.width, rect.height)
        })

        observer.observe(root, {
            attributes: true,
            attributeFilter: ["data-theme"],
        })

        return () => observer.disconnect()
    }, [])

    useEffect(() => {
        const canvas = canvasRef.current
        if (!canvas || width === 0 || height === 0) return

        const dpr = window.devicePixelRatio || 1

        canvas.width = width * dpr
        canvas.height = height * dpr

        const ctx = canvas.getContext("2d")
        if (!ctx) return

        ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    }, [width, height])


    // maybe not needed, assess later
    useEffect(() => {
        const handleResize = () => {
            // force layout reflow read
            const el = containerRef.current
            if (!el) return

            el.getBoundingClientRect() // forces recalculation
        }

        window.addEventListener("resize", handleResize)

        return () => window.removeEventListener("resize", handleResize)
    }, [])

    return (
        <div ref={containerRef} className={styles.root}>
            <canvas ref={canvasRef} {...bind}/>
            <div className={styles.debug}>
                start: {viewport.start.toFixed(2)}<br />
                end: {viewport.end.toFixed(2)}<br />
                duration: {duration.toFixed(2)}s
            </div>
        </div>
    )
}
