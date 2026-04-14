import { useState } from "react"
import { useAppStore } from "../../store/useAppStore"
import { loadReport } from "../../features/report/loadReport"
import styles from "./TopBar.module.css"

function nowUs() {
    return Date.now() * 1000
}

function toInputValue(us: number) {
    const d = new Date(us / 1000)
    return d.toISOString().slice(0, 16)
}

function fromInputValue(value: string) {
    return new Date(value).getTime() * 1000
}

export default function ReportControls() {

    const measurementId = useAppStore((s) => s.context.measurementId)
    const setReport = useAppStore((s) => s.setReport)
    const setReportLoading = useAppStore((s) => s.setReportLoading)

    const [start, setStart] = useState("")
    const [end, setEnd] = useState("")

    const valid =
        measurementId !== null &&
        start &&
        end &&
        fromInputValue(start) < fromInputValue(end)

    function applyRange(startUs: number, endUs: number) {
        setStart(toInputValue(startUs))
        setEnd(toInputValue(endUs))
    }

    function presetLast1h() {
        const end = nowUs()
        const start = end - 3600 * 1_000_000
        applyRange(start, end)
    }

    function presetToday() {
        const now = new Date()
        const start = new Date(
            now.getFullYear(),
            now.getMonth(),
            now.getDate()
        ).getTime() * 1000

        const end = nowUs()
        applyRange(start, end)
    }

    function presetWeek() {
        const end = nowUs()
        const start = end - 7 * 24 * 3600 * 1_000_000
        applyRange(start, end)
    }

    function presetMonth() {
        const end = nowUs()
        const start = end - 31 * 24 * 3600 * 1_000_000
        applyRange(start, end)
    }

    async function handleGenerate() {
        if (!valid || measurementId === null) return

        const startUs = fromInputValue(start)
        const endUs = fromInputValue(end)

        setReportLoading(true)

        try {
            const adapted = await loadReport({
                measurementId,
                startTimeUs: startUs,
                endTimeUs: endUs,
            })

            setReport(
                adapted.incidentsByModality,
                adapted.startTimeUs,
                adapted.endTimeUs,
            )
        } finally {
            setReportLoading(false)
        }
    }

    return (
        <div className={styles.controlsRow}>

            <button className={styles.btn} onClick={presetLast1h}>1h</button>
            <button className={styles.btn} onClick={presetToday}>Today</button>
            <button className={styles.btn} onClick={presetWeek}>7d</button>
            <button className={styles.btn} onClick={presetMonth}>1m</button>

            <input
                className={styles.input}
                type="datetime-local"
                value={start}
                onChange={(e) => setStart(e.target.value)}
            />

            <span>—</span>

            <input
                className={styles.input}
                type="datetime-local"
                value={end}
                onChange={(e) => setEnd(e.target.value)}
            />

            <button
                className={styles.btn}
                disabled={!valid}
                onClick={handleGenerate}
            >
                Generate
            </button>
        </div>
    )
}
