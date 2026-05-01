import { useAppStore } from "../../store/useAppStore"
import styles from "./WhitelistView.module.css"

export function SSIDRow({ ssid }: { ssid: string }) {
    const active = useAppStore(s => s.whitelistUI.active)
    const mode = useAppStore(s => s.whitelistUI.mode)
    const hover = useAppStore(s => s.hover.whitelist)

    const setActive = useAppStore(s => s.setWhitelistActive)
    const hoverWhitelist = useAppStore(s => s.hoverWhitelist)

    const isActive =
        active.type === "ssid" &&
        active.ssid === ssid

    const isBlockingMode =
        mode === "editing" || mode === "confirm-delete"
    const isDisabled =
        isBlockingMode && !isActive

    const isHovered =
        hover.type === "ssid" &&
        hover.ssid === ssid

    return (
        <div
            className={styles.row}
            data-selected={isActive || undefined}
            data-hovered={isHovered || undefined}
            data-disabled={isDisabled || undefined}
            onClick={() => {
                if (isDisabled) return

                setActive({
                    type: "ssid",
                    ssid,
                    bssid: null
                })
            }}
            onMouseEnter={() =>
                hoverWhitelist({
                    type: "ssid",
                    ssid,
                    bssid: null
                })
            }
            onMouseLeave={() => hoverWhitelist(null)}
        >
            <div className={styles.indent} />

            <div className={styles.icon}>📶</div>

            <div className={styles.chevron}>▼</div>

            <div className={styles.label} title={ssid}>
                {ssid}
            </div>

            <div className={styles.actions}>
                <button className={styles.btn}>✎</button>
                <button className={styles.btn}>🗑</button>
                <button className={styles.btn}>+</button>
            </div>
        </div>
    )
}
