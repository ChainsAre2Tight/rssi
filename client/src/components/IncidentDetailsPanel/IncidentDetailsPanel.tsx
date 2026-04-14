import IncidentHeader from "./IncidentHeader"
import WarningTimeline from "./WarningTimeline"

import HorizontalResizer from "../Layout/HorizontalResizer"

import styles from "./IncidentDetailsPanel.module.css"

import { useAppStore } from "../../store/useAppStore"
import WarningSplitPanel from "./WarningSplitPanel"

export default function IncidentDetailsPanel() {

    const warningTimelineHeight = useAppStore(
        (s) => s.layout.warningTimelineHeight
    )

    const setLayout = useAppStore((s) => s.setLayout)

    function resizeTimeline(delta: number) {

        setLayout((prev) => ({
            ...prev,
            warningTimelineHeight: Math.max(
                100,
                prev.warningTimelineHeight + delta
            )
        }))
    }

    return (

        <div className={styles.root}>

            <IncidentHeader />

            <div
                className={styles.timeline}
                style={{ height: warningTimelineHeight }}
            >
                <WarningTimeline />
            </div>

            <HorizontalResizer onDrag={resizeTimeline} />

            <div className={styles.details}>
                <WarningSplitPanel />
            </div>

        </div>

    )
}