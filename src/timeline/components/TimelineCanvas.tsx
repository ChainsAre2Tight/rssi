import { useEffect, useRef } from "react"
import { useContainerSize } from "../hooks/useContainerSize"
import { useViewport } from "../hooks/useViewport"
import { getNiceStep } from "../utils/timeGrid"
import styles from "./TimelineCanvas.module.css"

export default function TimelineCanvas() {
    const containerRef = useRef<HTMLDivElement | null>(null)
    const canvasRef = useRef<HTMLCanvasElement | null>(null)

    const { width, height } = useContainerSize(containerRef as React.RefObject<HTMLDivElement>)
    const { viewport, duration } = useViewport()

    // sync canvas resolution
    useEffect(() => {
        const canvas = canvasRef.current
        if (!canvas || width === 0 || height === 0) return

        const dpr = window.devicePixelRatio || 1

        canvas.width = width * dpr
        canvas.height = height * dpr

        canvas.style.width = `${width}px`
        canvas.style.height = `${height}px`

        const ctx = canvas.getContext("2d")
        if (!ctx) return

        ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

        // use theme token
        ctx.fillStyle = getComputedStyle(document.documentElement)
            .getPropertyValue("--color-bg")

        ctx.fillRect(0, 0, width, height)

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

        ctx.lineWidth = 1

        for (let t = firstTick; t < end; t += step) {
            const x = Math.round((t - start) * scale) + 0.5

            ctx.beginPath()
            ctx.moveTo(x, 0)
            ctx.lineTo(x, height)
            ctx.stroke()
        }
    }, [width, height, viewport.start, viewport.end])

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

    return (
        <div ref={containerRef} className={styles.root}>
            <canvas ref={canvasRef} />
        </div>
    )
}
