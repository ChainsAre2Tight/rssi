import { useRef, useEffect, useCallback, useState } from "react"
import type { RefObject } from "react"
import { useAppStore } from "../../store/useAppStore"
import { useMapViewport } from "../hooks/useMapViewport"
import { useMapInteraction } from "../hooks/useMapInteraction"
import { useMapRenderer } from "../hooks/useMapRenderer"
import { buildLocalizationAdapter } from "../adapters/localization"
import { fetchSensors } from "../../services/localizationApi"
import { fitBounds, canvasToWorld } from "../utils/geometry"
import styles from "./MapView.module.css"

export default function MapView() {
    const containerRef = useRef<HTMLDivElement | null>(null)
    const canvasRef = useRef<HTMLCanvasElement | null>(null) as RefObject<HTMLCanvasElement>

    const [width, setWidth] = useState(0)
    const [height, setHeight] = useState(0)

    const measurementId = useAppStore(s => s.context.measurementId)
    const incidentId = useAppStore(s => s.selection.incidentId)
    const { cache, sensors } = useAppStore(s => s.localization)
    const { setSensors } = useAppStore()

    const localizationData = incidentId ? cache[incidentId] : null

    // Resize observer for canvas
    useEffect(() => {
        const updateSize = () => {
            if (containerRef.current) {
                setWidth(containerRef.current.clientWidth)
                setHeight(containerRef.current.clientHeight)
            }
        }

        const observer = new ResizeObserver(updateSize)
        if (containerRef.current) {
            observer.observe(containerRef.current)
            updateSize()
        }

        return () => observer.disconnect()
    }, [])

    // Build adapter from localization data
    const adapter = localizationData
        ? buildLocalizationAdapter({
            locations: localizationData.locations,
            sensors: sensors[String(measurementId)] || [],
        })
        : null

    // Initialize viewport from adapter bounds
    const { viewport, setViewport } = useMapViewport(
        adapter?.bounds
    )

    // Update viewport when adapter changes
    useEffect(() => {
        if (adapter?.bounds) {
            setViewport(fitBounds(adapter.bounds, 0.15))
        }
    }, [adapter?.bounds, setViewport])

    // Fetch sensors on mount
    useEffect(() => {
        if (!measurementId || sensors[String(measurementId)]) return

        fetchSensors(measurementId)
            .then(sensorsData => setSensors(measurementId, sensorsData))
            .catch(() => {})
    }, [measurementId, sensors, setSensors])

    // Interaction
    const { bind, cursor } = useMapInteraction({
        viewport,
        setViewport,
        canvasWidth: width,
        canvasHeight: height,
    })

    // Rendering
    useMapRenderer({
        canvasRef,
        width,
        height,
        viewport,
        adapter: adapter || { segments: [], sensors: [], bounds: { minX: 0, maxX: 10, minY: 0, maxY: 10 } },
    })

    const handleZoomIn = useCallback(() => {
        setViewport(prev => {
            const center = (prev.minX + prev.maxX) / 2
            const centerY = (prev.minY + prev.maxY) / 2
            const width = prev.maxX - prev.minX
            const height = prev.maxY - prev.minY

            return {
                minX: center - (width * 0.25),
                maxX: center + (width * 0.25),
                minY: centerY - (height * 0.25),
                maxY: centerY + (height * 0.25),
            }
        })
    }, [setViewport])

    const handleZoomOut = useCallback(() => {
        setViewport(prev => {
            const center = (prev.minX + prev.maxX) / 2
            const centerY = (prev.minY + prev.maxY) / 2
            const width = prev.maxX - prev.minX
            const height = prev.maxY - prev.minY

            return {
                minX: center - width,
                maxX: center + width,
                minY: centerY - height,
                maxY: centerY + height,
            }
        })
    }, [setViewport])

    const handleFitAll = useCallback(() => {
        if (!adapter) return
        setViewport(fitBounds(adapter.bounds, 0.15))
    }, [adapter, setViewport])

    // Calculate cursor world position for debug
    const cursorWorldPos = cursor.current
        ? canvasToWorld(cursor.current.x, cursor.current.y, viewport, width, height)
        : null

    // Find Z coordinate at cursor position (from adapter segments)
    let cursorZ: number | null = null
    if (cursorWorldPos && adapter) {
        for (const seg of adapter.segments) {
            for (const pt of seg.points) {
                if (Math.abs(pt.x - cursorWorldPos.x) < 0.1 && Math.abs(pt.y - cursorWorldPos.y) < 0.1) {
                    cursorZ = pt.z
                    break
                }
            }
        }
    }

    if (!localizationData) {
        return (
            <div className={styles.placeholder}>
                No localization data loaded
            </div>
        )
    }

    return (
        <div ref={containerRef} className={styles.root}>
            <canvas
                ref={canvasRef}
                width={width}
                height={height}
                {...bind}
                className={styles.canvas}
            />

            <div className={styles.debug}>
                x: {cursorWorldPos ? cursorWorldPos.x.toFixed(2) : "-"}m<br />
                y: {cursorWorldPos ? cursorWorldPos.y.toFixed(2) : "-"}m<br />
                z: {cursorZ !== null ? cursorZ.toFixed(2) : "-"}m<br />
            </div>

            <div className={styles.controls}>
                <button className={styles.controlBtn} onClick={handleZoomIn} title="Zoom in">
                    ＋
                </button>

                <button className={styles.controlBtn} onClick={handleZoomOut} title="Zoom out">
                    －
                </button>

                <div className={styles.separator} />

                <button className={styles.controlBtn} onClick={handleFitAll} title="Fit all">
                    ⤢
                </button>
            </div>
        </div>
    )
}
