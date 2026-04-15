import { useRef, useEffect, type RefObject, useState } from "react"
import { useContainerSize } from "../hooks/useContainerSize"
import { useViewport } from "../hooks/useViewport"
import { useTimelineInteraction } from "../hooks/useTimelineInteraction"
import { useTimelineRenderer } from "../hooks/useTimelineRenderer"
import { useTrackResizing } from "../hooks/useTrackResizing"
import { computeTrackLayout } from "../utils/trackLayout"
import type { TimelineAdapterResult, TimelineTrack } from "../types"
import styles from "./TimelineCanvas.module.css"
import { createTimeMapper, hitTest } from "../utils/mapping"
import { ensureVisible, getSafeBoundsViewport } from "../utils/ensureVisible"
import { useTimelineSync } from "../hooks/useTimelineSync"
import { useTimelineHoverSync } from "../hooks/useTimelineHoverSync"
import { formatDateTime } from "../../utils/time"
import { computeItemsBounds } from "../utils/zoomToFit"
import { zoomViewport } from "../utils/zoomViewport"


export default function TimelineCanvas(params: {
    adapter: TimelineAdapterResult
    viewportResetKey?: string | number
    externalSelectedKey: string | null
    onSelect: (item: { key: string; type: "incident" | "warning"; id: string } | null) => void
    externalHoverKey?: string | null
    externalHoverTimeUs?: number | null
    onHoverItem?: (item: any | null) => void
    onHoverTime?: (timeUs: number | null) => void
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

    const [hoveredKey, setHoveredKey] = useState<string | null>(null)
    const [externalCursorTimeUs, setExternalCursorTimeUs] = useState<number | null>(null)

    const { handleInternalHover } = useTimelineHoverSync({
        adapter: params.adapter,

        externalHoverKey: params.externalHoverKey ?? null,
        externalHoverTimeUs: params.externalHoverTimeUs ?? null,

        onHoverItem: params.onHoverItem ?? (() => {}),
        onHoverTime: params.onHoverTime ?? (() => {}),

        setHoveredKey,
        setExternalCursorTimeUs,
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
                
                if (!item) {
                    handleInternalSelect(null)
                    return
                }
                handleInternalSelect(item.key !== params.externalSelectedKey ? item.key : null)
            },
            onMove: (x, y) => {
                const item = hitTest(
                    x,
                    y,
                    width,
                    viewport,
                    layout,
                    params.adapter.itemsByTrack
                )

                // idk why that works...
                const mapper = createTimeMapper(viewport, width, 0)
                const time = mapper.toTime(x)
                const timeUs = mapper.toGlobalUs(time)

                handleInternalHover(item ? item.key : null, timeUs)
            },
        })

    const HEADER_HEIGHT = 28
    const DEFAULT_EXPANDED_HEIGHT = 120

    const [tracks, setTracks] = useState<TimelineTrack[]>([])

    useEffect(() => {
        if (params.adapter.trackIds.length === 1) {
            const tracks: TimelineTrack[] = params.adapter.trackIds.map(id => ({
                id,
                label: id,
                height: 500,
                collapsible: false,
                resizable: true,
                lastExpandedHeight: 500,
            }))
            setTracks(tracks)
            return
        }

        const nextTracks: TimelineTrack[] = params.adapter.trackIds.map(id => ({
            id,
            label: id,
            height: 200,
            collapsible: true,
            resizable: true,
            lastExpandedHeight: 100,
        }))

        setTracks(nextTracks)
    }, [params.adapter.itemsByTrack])

    useEffect(() => {
        if (!params.adapter.bounds.start || !params.adapter.bounds.end) return

        const start = params.adapter.bounds.start / 1_000_000
        const end = params.adapter.bounds.end / 1_000_000

        setViewport(getSafeBoundsViewport(start, end, 0.15))
    }, [params.viewportResetKey])

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

    const hoveredItem = hoveredKey
        ? params.adapter.index.byKey.get(hoveredKey)
        : cursor.current
            ? hitTest(
                cursor.current.x,
                cursor.current.y,
                width,
                viewport,
                layout,
                params.adapter.itemsByTrack,
            )
            : null
    
    function handleResetView() {
        const start = params.adapter.bounds.start / 1_000_000
        const end = params.adapter.bounds.end / 1_000_000

        setViewport(getSafeBoundsViewport(start, end, 0.15))
    }

    function handleZoomToFit() {
        const bounds = computeItemsBounds(params.adapter)

        if (!bounds) {
            handleResetView()
            return
        }

        setViewport(getSafeBoundsViewport(bounds.start, bounds.end, 0.15))
    }

    function handleZoomIn() {
        setViewport(prev =>
            zoomViewport({
                viewport: prev,
                zoomFactor: 0.5,
            })
        )
    }

    function handleZoomOut() {
        setViewport(prev =>
            zoomViewport({
                viewport: prev,
                zoomFactor: 2,
            })
        )
    }

    useTimelineRenderer({
        canvasRef,
        width,
        height,
        viewport,
        cursor,
        zoomAnchorX,
        isZooming,
        tracks: layout,
        adapter: params.adapter,
        selectedItem: selectedItem ? selectedItem : null,
        hoveredItem,
        externalCursorTimeUs: cursor.current ? null : externalCursorTimeUs,
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

                {!params.adapter.hasItems && (
                    <div className={styles.placeholderOverlay}>
                        No incidents loaded
                    </div>
                )}

                <div className={styles.debug}>
                    start: {formatDateTime(viewport.start*1_000_000)}<br />
                    end: {formatDateTime(viewport.end*1_000_000)}<br />
                    duration: {duration.toFixed(2)}s<br />
                    cursorTime: {formatDateTime(externalCursorTimeUs!)}
                </div>

                <div className={styles.controls}>

                    <button
                        className={styles.controlBtn}
                        onClick={handleZoomIn}
                        title="Zoom in"
                    >
                        ＋
                    </button>

                    <button
                        className={styles.controlBtn}
                        onClick={handleZoomOut}
                        title="Zoom out"
                    >
                        －
                    </button>

                    <div className={styles.separator} />

                    <button
                        className={styles.controlBtn}
                        onClick={handleResetView}
                        title="Reset view"
                    >
                        ⟲
                    </button>

                    <button
                        className={styles.controlBtn}
                        onClick={handleZoomToFit}
                        title="Zoom to fit"
                    >
                        ⤢
                    </button>
                </div>
            </div>
        </div>
    )
}