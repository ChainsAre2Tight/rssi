import { useAppStore } from "../../store/useAppStore"
import { loadReport } from "../../features/report/loadReport"

export default function ActiveControls() {

    const measurementId = useAppStore(s => s.context.measurementId)
    const offsetS = useAppStore(s => s.active.offsetS)

    const setOffset = useAppStore(s => s.setActiveOffset)
    const setReport = useAppStore(s => s.setReport)
    const setLoading = useAppStore(s => s.setReportLoading)

    async function handleLoad() {
        if (measurementId === null) return

        setLoading(true)

        try {
            const adapted = await loadReport({
                measurementId,
                offsetS,
            })

            setReport(
                adapted.incidentsByModality,
                adapted.startTimeUs,
                adapted.endTimeUs
            )
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="controlsRow">

            <button onClick={() => setOffset(300)}>5m</button>
            <button onClick={() => setOffset(900)}>15m</button>
            <button onClick={() => setOffset(3600)}>1h</button>
            <button onClick={() => setOffset(21600)}>6h</button>

            <button
                disabled={measurementId === null}
                onClick={handleLoad}
            >
                Load
            </button>
        </div>
    )
}
