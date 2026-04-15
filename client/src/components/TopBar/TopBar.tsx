import { useEffect, useRef } from "react"
import styles from "./TopBar.module.css"

import { useAppStore } from "../../store/useAppStore"

import MeasurementSelector from "./MeasurementSelector"
import ModeToggle from "./ModeToggle"
import ReportControls from "./ReportControls"
import ActiveControls from "./ActiveControls"

import { formatDateTime } from "../../utils/time"

export default function TopBar() {
    const mode = useAppStore((s) => s.context.mode)
    const startUs = useAppStore((s) => s.report.startTimeUs)
    const endUs = useAppStore((s) => s.report.endTimeUs)

    const query = useAppStore((s) => s.filters.query)
    const setQuery = useAppStore((s) => s.setSearchQuery)

    const inputRef = useRef<HTMLInputElement | null>(null)

    const hasData = startUs && endUs

    // 🔥 Ctrl/Cmd + F focus
    useEffect(() => {
        function handleKey(e: KeyboardEvent) {
            if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "f") {
                e.preventDefault()
                inputRef.current?.focus()
                inputRef.current?.select()
            }

            if (e.key === "Escape") {
                inputRef.current?.blur()
            }
        }

        window.addEventListener("keydown", handleKey)
        return () => window.removeEventListener("keydown", handleKey)
    }, [])

    return (
        <div className={styles.root}>
            <div className={styles.left}>
                <div className={styles.group}>
                    <MeasurementSelector />
                </div>

                <div className={styles.group}>
                    <ModeToggle />
                </div>

                <div className={styles.group}>
                    {mode === "active" && <ActiveControls />}
                    {mode === "report" && <ReportControls />}
                </div>
            </div>

            <div className={styles.middle}>
                {hasData ? (
                    <>
                        {formatDateTime(startUs)}
                        {" — "}
                        {formatDateTime(endUs)}
                    </>
                ) : (
                    <span className={styles.empty}>
                        No data loaded
                    </span>
                )}
            </div>

            <div className={styles.right}>
                <div className={styles.search}>
                    <input
                        ref={inputRef}
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        className={styles.input}
                        placeholder="Search (signal, detector, identity...)"
                    />

                    {query && (
                        <button
                            className={styles.clear}
                            onClick={() => setQuery("")}
                            title="Clear"
                        >
                            ✕
                        </button>
                    )}
                </div>
            </div>
        </div>
    )
}
