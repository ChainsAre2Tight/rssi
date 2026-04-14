import { useEffect, useRef } from "react"

import { useAppStore } from "../../store/useAppStore"

import { fetchActiveReport } from "../../services/reportApi"
import { adaptReport } from "../../features/report/adapter"
import type { BackendReport } from "../../types/backend"

export default function ActiveControls() {

    const measurementId = useAppStore((s) => s.context.measurementId)

    const running = useAppStore((s) => s.active.running)
    const offsetS = useAppStore((s) => s.active.offsetS)

    const setRunning = useAppStore((s) => s.setActiveRunning)
    const setOffset = useAppStore((s) => s.setActiveOffset)

    const setReport = useAppStore((s) => s.setReport)

    const intervalRef = useRef<number | null>(null)

    async function poll() {

        if (measurementId === null) {
            return
        }

        try {

            const raw = await fetchActiveReport({
                measurementId,
                offsetS
            })

            const adapted = adaptReport(raw as BackendReport)

            setReport(
                adapted.incidentsByModality,
                adapted.startTimeUs as unknown as number,
                adapted.endTimeUs
            )

        } catch (err) {
            console.error("Active polling failed", err)
        }
    }

    function start() {
        console.log("123")

        if (running || measurementId === null) {
            return
        }

        setRunning(true)

        poll()

        intervalRef.current = window.setInterval(poll, 2000)
    }

    function stop() {

        setRunning(false)

        if (intervalRef.current !== null) {
            clearInterval(intervalRef.current)
            intervalRef.current = null
        }
    }

    useEffect(() => {
        return () => {
            if (intervalRef.current !== null) {
                clearInterval(intervalRef.current)
            }
        }
    }, [])

    return (
        <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>

            <input
                type="number"
                value={offsetS}
                onChange={(e) => setOffset(Number(e.target.value))}
            />

            {!running && (
                <button
                    disabled={measurementId === null}
                    onClick={start}
                >
                    Start
                </button>
            )}

            {running && (
                <button
                    style={{ background: "#c0392b", color: "white" }}
                    onClick={stop}
                >
                    Stop
                </button>
            )}

        </div>
    )
}
