import styles from "./TopBar.module.css"

import { useAppStore } from "../../store/useAppStore"

import MeasurementSelector from "./MeasurementSelector"
import ModeToggle from "./ModeToggle"
import ReportControls from "./ReportControls"

export default function TopBar() {

    const mode = useAppStore((s) => s.context.mode)

    return (
        <div className={styles.root}>

            <div className={styles.left}>
                <MeasurementSelector />
                <ModeToggle />
            </div>

            <div className={styles.right}>
                {mode === "report" && <ReportControls />}
            </div>

        </div>
    )
}