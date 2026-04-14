import { useAppStore } from "../../store/useAppStore"

export default function ModeToggle() {

    const mode = useAppStore((s) => s.context.mode)
    const setMode = useAppStore((s) => s.setMode)

    return (
        <div>
            <button
                disabled={mode === "active"}
                onClick={() => setMode("active")}
            >
                Active
            </button>

            <button
                disabled={mode === "report"}
                onClick={() => setMode("report")}
            >
                Report
            </button>
        </div>
    )
}