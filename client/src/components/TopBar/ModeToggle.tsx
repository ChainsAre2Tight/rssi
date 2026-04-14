import { useAppStore } from "../../store/useAppStore"
import styles from "./ModeToggle.module.css"

export default function ModeToggle() {

    const mode = useAppStore((s) => s.context.mode)
    const setMode = useAppStore((s) => s.setMode)

    return (
        <div className={styles.toggle}>
            <button
                data-active={mode === "active"}
                onClick={() => setMode("active")}
            >
                Active
            </button>

            <button
                data-active={mode === "report"}
                onClick={() => setMode("report")}
            >
                Report
            </button>
        </div>
    )
}
