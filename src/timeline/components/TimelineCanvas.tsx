import { useRef, useEffect, type RefObject } from "react"
import { useContainerSize } from "../hooks/useContainerSize"
import { useViewport } from "../hooks/useViewport"
import { useTimelineInteraction } from "../hooks/useTimelineInteraction"
import { useTimelineRenderer } from "../hooks/useTimelineRenderer"
import { getNiceStep } from "../utils/timeGrid"
import { computeTrackLayout } from "../utils/trackLayout"
import type { TimelineTrack } from "../types/types"
import styles from "./TimelineCanvas.module.css"

export default function TimelineCanvas() {
    const containerRef = useRef<HTMLDivElement | null>(null)
    const canvasRef = useRef<HTMLCanvasElement | null>(null) as RefObject<HTMLCanvasElement>

    const { width, height } = useContainerSize(containerRef as React.RefObject<HTMLDivElement>)
    const { viewport, setViewport, duration } = useViewport()

    const { bind, cursorX, zoomAnchorX, isZooming } =
        useTimelineInteraction({
            viewport,
            setViewport,
            width,
        })

    const tracks: TimelineTrack[] = [
        {
            id: "modality-1",
            label: "Modality A",
            height: 120,
            collapsible: true,
            collapsed: false,
        },
        {
            id: "modality-2",
            label: "Modality B",
            height: 120,
            collapsible: true,
            collapsed: false,
        },
    ]

    const layout = computeTrackLayout(tracks)

    useTimelineRenderer({
        canvasRef,
        width,
        height,
        viewport,
        cursorX,
        zoomAnchorX,
        isZooming,
        getNiceStep,
        tracks: layout,
    })

    useEffect(() => {
        const root = document.documentElement

        const observer = new MutationObserver(() => {
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
            <div className={styles.tracksOverlay}>
                {layout.map((t) => {
                    if (!t.visible || !t.track.label) return null

                    return (
                        <div
                            key={t.id}
                            className={styles.trackHeader}
                            style={{
                                top: t.y,
                                height: t.height,
                            }}
                        >
                            {t.track.label}
                        </div>
                    )
                })}
            </div>

            <canvas ref={canvasRef} {...bind} />

            <div className={styles.debug}>
                start: {viewport.start.toFixed(2)}<br />
                end: {viewport.end.toFixed(2)}<br />
                duration: {duration.toFixed(2)}s
            </div>
        </div>
    )
}