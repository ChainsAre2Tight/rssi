import { useAppStore } from "../../store/useAppStore"
import { loadReport } from "../../features/report/loadReport"
import styles from "./TopBar.module.css"

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
        <div className={styles.controlsRow}>

            {/* offset presets */}
            <button
                className={styles.btn}
                data-active={offsetS === 300}
                onClick={() => setOffset(300)}
            >
                5m
            </button>

            <button
                className={styles.btn}
                data-active={offsetS === 900}
                onClick={() => setOffset(900)}
            >
                15m
            </button>

            <button
                className={styles.btn}
                data-active={offsetS === 3600}
                onClick={() => setOffset(3600)}
            >
                1h
            </button>

            <button
                className={styles.btn}
                data-active={offsetS === 21600}
                onClick={() => setOffset(21600)}
            >
                6h
            </button>

            {/* action */}
            <button
                className={styles.btn}
                disabled={measurementId === null}
                onClick={handleLoad}
            >
                Load
            </button>
        </div>
    )
}
