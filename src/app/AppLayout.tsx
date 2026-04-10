import styles from "./AppLayout.module.css"

import TopBar from "../components/TopBar/TopBar"
import GlobalTimeline from "../components/Timeline/GlobalTimeline"
import ExplorerPanel from "../components/ExplorerPanel/ExplorerPanel"
import IncidentDetailsPanel from "../components/IncidentDetailsPanel/IncidentDetailsPanel"

import { useEffect } from "react"
import { loadMockReport } from "../features/report/mockReport"
import { useAppStore } from "../store/useAppStore"


export default function AppLayout() {

    const setReport = useAppStore((s) => s.setReport)

    useEffect(() => {
        const report = loadMockReport()

        setReport(
            report.incidentsByModality,
            report.startTimeUs ?? 0,
            report.endTimeUs
        )
    }, [])

    return (
        <div className={styles.root}>
            <div className={styles.topbar}>
                <TopBar />
            </div>

            <div className={styles.timeline}>
                <GlobalTimeline />
            </div>

            <div className={styles.main}>
                <div className={styles.explorer}>
                    <ExplorerPanel />
                </div>

                <div className={styles.details}>
                    <IncidentDetailsPanel />
                </div>
            </div>
        </div>
    )
}