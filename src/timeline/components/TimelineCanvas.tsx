import { useRef, useEffect, type RefObject, useState } from "react"
import { useContainerSize } from "../hooks/useContainerSize"
import { useViewport } from "../hooks/useViewport"
import { useTimelineInteraction } from "../hooks/useTimelineInteraction"
import { useTimelineRenderer } from "../hooks/useTimelineRenderer"
import { useTrackResizing } from "../hooks/useTrackResizing"
import { getNiceStep } from "../utils/timeGrid"
import { computeTrackLayout } from "../utils/trackLayout"
import type { TimelineAdapterResult, TimelineItem, TimelineTrack } from "../types"
import styles from "./TimelineCanvas.module.css"
import { hitTest } from "../utils/mapping"
import { ensureVisible } from "../utils/ensureVisible"
import { useTimelineSync } from "../hooks/useTimelineSync"


export default function TimelineCanvas(params: {
    adapter: TimelineAdapterResult
    externalSelectedKey: string | null
    onSelect: (item: { key: string; type: "incident" | "warning"; id: string } | null) => void
}) {
    const containerRef = useRef<HTMLDivElement | null>(null)
    const canvasRef = useRef<HTMLCanvasElement | null>(null) as RefObject<HTMLCanvasElement>

    const { width, height } = useContainerSize(containerRef as React.RefObject<HTMLDivElement>)
    const { viewport, setViewport, duration } = useViewport()
    
    const [selectedKey, setSelectedKey] = useState<string | null>(null)
    const { handleInternalSelect } = useTimelineSync({
        adapter: params.adapter,
        externalSelectedKey: params.externalSelectedKey,
        onSelect: params.onSelect,
        setSelectedKey,
    })

    const { bind, cursor, zoomAnchorX, isZooming } =
        useTimelineInteraction({
            viewport,
            setViewport,
            width,
            onClick: (x, y) => {
                const item = hitTest(
                    x,
                    y,
                    width,
                    viewport,
                    layout,
                    params.adapter.itemsByTrack
                )

                handleInternalSelect(item ? item.key : null)
            }
        })

    const HEADER_HEIGHT = 28
    const DEFAULT_EXPANDED_HEIGHT = 120

    const [tracks, setTracks] = useState<TimelineTrack[]>([])

    useEffect(() => {
        const nextTracks: TimelineTrack[] = params.adapter.trackIds.map(id => ({
            id,
            label: id,
            height: 100,
            collapsible: true,
            resizable: true,
            lastExpandedHeight: 100,
        }))

        setTracks(nextTracks)
    }, [params.adapter.itemsByTrack])

    const initializedRef = useRef(false)

    useEffect(() => {
        if (initializedRef.current) return
        if (!params.adapter.bounds.start || !params.adapter.bounds.end) return

        setViewport({
            start: params.adapter.bounds.start / 1_000_000,
            end: params.adapter.bounds.end / 1_000_000,
        })

        initializedRef.current = true
    }, [params.adapter.bounds.start, params.adapter.bounds.end])

    const layout = computeTrackLayout(tracks)

    function toggleTrack(id: string) {
        setTracks(prev =>
            prev.map(t => {
                if (t.id !== id || !t.collapsible) return t

                const isCollapsed = t.height <= HEADER_HEIGHT

                if (isCollapsed) {
                    return {
                        ...t,
                        height: t.lastExpandedHeight ?? DEFAULT_EXPANDED_HEIGHT,
                    }
                }

                return {
                    ...t,
                    lastExpandedHeight: t.height,
                    height: HEADER_HEIGHT,
                }
            })
        )
    }

    useEffect(() => {
        if (!selectedKey) return

        const item = params.adapter.index.byKey.get(selectedKey)
        if (!item) return

        setViewport(prev =>
            ensureVisible({
                viewport: prev,
                itemStart: item.start,
                itemEnd: item.end,
            })
        )
    }, [selectedKey])

    const resizing = useTrackResizing({
        layout,
        tracks,
        setTracks,
    })

    const selectedItem = selectedKey
        ? params.adapter.index.byKey.get(selectedKey)
        : null

    useTimelineRenderer({
        canvasRef,
        width,
        height,
        viewport,
        cursor,
        zoomAnchorX,
        isZooming,
        getNiceStep,
        tracks: layout,
        adapter: params.adapter,
        selectedItem: selectedItem ? selectedItem : null,
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
            {/* LEFT: HEADERS */}
            <div className={styles.headersColumn}>
                {layout.map((t) => {
                    if (!t.track.label) return null

                    return (
                        <div
                            key={t.id}
                            className={styles.trackHeader}
                            style={{
                                top: t.y,
                                height: 28,
                            }}
                            onClick={() => toggleTrack(t.id)}
                        >
                            <span className={styles.chevron}>
                                {t.track.collapsible
                                    ? t.track.height <= HEADER_HEIGHT ? "▶" : "▼"
                                    : null}
                            </span>

                            {t.track.label}
                        </div>
                    )
                })}
            </div>

            {/* RIGHT: CANVAS */}
            <div
                className={styles.canvasColumn}
                ref={containerRef}
                {...resizing.bind}
            >
                <canvas ref={canvasRef} {...bind} />

                <div className={styles.debug}>
                    start: {viewport.start.toFixed(2)}<br />
                    end: {viewport.end.toFixed(2)}<br />
                    duration: {duration.toFixed(2)}s
                </div>
            </div>
        </div>
    )
}