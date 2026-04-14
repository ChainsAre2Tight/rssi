import { useAppStore } from "../../store/useAppStore"
import VerticalResizer from "../Layout/VerticalResizer"

import WarningDetailsList from "./WarningDetailsList"
// later this becomes WarningList
// and details will move out

import styles from "./WarningSplitPanel.module.css"

export default function WarningSplitPanel() {

    const warningListWidth = useAppStore(
        (s) => s.layout.warningListWidth
    )

    const setLayout = useAppStore((s) => s.setLayout)

    function resize(delta: number) {
        setLayout((prev) => ({
            ...prev,
            warningListWidth: Math.max(
                200,
                prev.warningListWidth + delta
            )
        }))
    }

    return (
        <div className={styles.root}>

            <div
                className={styles.left}
                style={{ width: warningListWidth }}
            >
                <WarningDetailsList />
            </div>

            <VerticalResizer onDrag={resize} />

            <div className={styles.right}>
                {/* placeholder for now */}
                <div className={styles.placeholder}>
                    Select a warning to see details
                </div>
            </div>

        </div>
    )
}