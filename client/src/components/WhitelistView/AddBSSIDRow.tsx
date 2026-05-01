import { useAppStore } from "../../store/useAppStore"
import styles from "./WhitelistView.module.css"

export function AddBSSIDRow({ ssid }: { ssid: string }) {
    const active = useAppStore(s => s.whitelistUI.active)
    const setActive = useAppStore(s => s.setWhitelistActive)
    const mode = useAppStore(s => s.whitelistUI.mode)

    const isActive =
        active.type === "add-bssid" &&
        active.ssid === ssid

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
                    type: "add-bssid",
                    ssid,
                    bssid: null
                })
            }}
        >
            <div className={styles.indent} />
            <div className={styles.indent} />

            <div className={styles.icon} />
            <div className={styles.chevron} />

            <div className={styles.label}>
                + Add BSSID
            </div>
        </div>
    )
}
