import { useState } from "react"

import { useAppStore } from "../../store/useAppStore"

import { fetchReport } from "../../services/reportApi"
import { adaptReport } from "../../features/report/adapter"

import type { BackendReport } from "../../types/backend"

export default function ReportControls() {

    const measurementId = useAppStore((s) => s.context.measurementId)
    const setReport = useAppStore((s) => s.setReport)
    const setReportLoading = useAppStore((s) => s.setReportLoading)

    const [startUs, setStartUs] = useState("")
    const [endUs, setEndUs] = useState("")

    const [pendingReport, setPendingReport] = useState<any>(null)

    const valid =
        measurementId !== null &&
        startUs !== "" &&
        endUs !== "" &&
        Number(startUs) < Number(endUs)

    async function handleGenerate() {

        if (!valid || measurementId === null) {
            return
        }

        const start = Number(startUs)
        const end = Number(endUs)

        setReportLoading(true)

        try {

            const raw = await fetchReport({
                measurementId,
                startTimeUs: start,
                endTimeUs: end
            })

            const adapted = adaptReport(raw as BackendReport)

            // store locally first
            setPendingReport(adapted)

            // commit immediately for now
            setReport(
                adapted.incidentsByModality,
                adapted.startTimeUs as unknown as number,
                adapted.endTimeUs
            )

        } catch (err) {
            console.error("Report fetch failed", err)
        } finally {
            setReportLoading(false)
        }
    }

    return (
        <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>

            <input
                type="number"
                placeholder="start_us"
                value={startUs}
                onChange={(e) => setStartUs(e.target.value)}
            />

            <input
                type="number"
                placeholder="end_us"
                value={endUs}
                onChange={(e) => setEndUs(e.target.value)}
            />

            <button
                disabled={!valid}
                onClick={handleGenerate}
            >
                Generate Report
            </button>

        </div>
    )
}
