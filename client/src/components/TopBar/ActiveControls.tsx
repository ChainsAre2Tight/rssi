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
        } catch (err) {
            console.error("Active load failed", err)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>

            <input
                type="number"
                value={offsetS}
                onChange={(e) => setOffset(Number(e.target.value))}
            />

            <button
                disabled={measurementId === null}
                onClick={handleLoad}
            >
                Load Active
            </button>

        </div>
    )
}