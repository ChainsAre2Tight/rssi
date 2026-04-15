import styles from "./AppLayout.module.css"

import TopBar from "../TopBar/TopBar.tsx"
import GlobalTimeline from "../Timeline/GlobalTimeline.tsx"
import ExplorerPanel from "../ExplorerPanel/ExplorerPanel.tsx"
import IncidentDetailsPanel from "../IncidentDetailsPanel/IncidentDetailsPanel.tsx"

import HorizontalResizer from "./HorizontalResizer"
import VerticalResizer from "./VerticalResizer.tsx"

import { useAppStore } from "../../store/useAppStore.ts"
import GlobalAreaContainer from "./GlobalAreaContainer.tsx"

export default function AppLayout() {

    const explorerWidth = useAppStore((s) => s.layout.explorerWidth)
    const timelineHeight = useAppStore((s) => s.layout.globalTimelineHeight)

    const setLayout = useAppStore((s) => s.setLayout)

    function resizeTimeline(delta: number) {

        setLayout((prev) => ({
            ...prev,
            globalTimelineHeight: Math.max(100, prev.globalTimelineHeight + delta)
        }))
    }

    function resizeExplorer(delta: number) {

        setLayout((prev) => ({
            ...prev,
            explorerWidth: Math.max(200, prev.explorerWidth + delta)
        }))
    }

    return (
        <div className={styles.root}>

            <div className={styles.topbar}>
                <TopBar />
            </div>

            <div
                className={styles.timeline}
                style={{ height: timelineHeight }}
            >
                <GlobalAreaContainer />
            </div>

            <HorizontalResizer onDrag={resizeTimeline} />

            <div className={styles.main}>

                <div
                    className={styles.explorer}
                    style={{ width: explorerWidth }}
                >
                    <ExplorerPanel />
                </div>

                <VerticalResizer onDrag={resizeExplorer} />

                <div className={styles.details}>
                    <IncidentDetailsPanel />
                </div>

            </div>

        </div>
    )
}