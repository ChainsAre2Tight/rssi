import { useAppStore } from "../../store/useAppStore"
import styles from "./WhitelistView.module.css"

export function AddSSIDRow() {
    const active = useAppStore(s => s.whitelistUI.active)
    const setActive = useAppStore(s => s.setWhitelistActive)
    const mode = useAppStore(s => s.whitelistUI.mode)

    const isActive = active.type === "add-ssid"
    const isBlockingMode =
        mode === "editing" || mode === "confirm-delete"
    const isDisabled =
        isBlockingMode && !isActive

    return (
        <div
            className={`${styles.row} ${styles.addRow}`}
            data-selected={isActive || undefined}
            data-disabled={isDisabled || undefined}
            onClick={() => {
                if (isDisabled) return

                setActive({
                    type: "add-ssid",
                    ssid: null,
                    bssid: null
                })
            }}
        >
            <div className={styles.indent} />
            <div className={styles.icon} />
            <div className={styles.chevron} />

            <div className={styles.label}>
                + Add SSID
            </div>
        </div>
    )
}