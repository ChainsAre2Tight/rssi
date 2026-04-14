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

    const hasData = startUs && endUs

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

            <div className={styles.right}>
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
        </div>
    )
}
