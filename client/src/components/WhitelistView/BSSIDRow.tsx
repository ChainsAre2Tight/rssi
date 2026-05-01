import { useAppStore } from "../../store/useAppStore"
import styles from "./WhitelistView.module.css"

export function BSSIDRow({
    ssid,
    bssid
}: {
    ssid: string
    bssid: string
}) {
    const active = useAppStore(s => s.whitelistUI.active)
    const hover = useAppStore(s => s.hover.whitelist)
    const mode = useAppStore(s => s.whitelistUI.mode)

    const setActive = useAppStore(s => s.setWhitelistActive)
    const hoverWhitelist = useAppStore(s => s.hoverWhitelist)

    const isActive =
        active.type === "bssid" &&
        active.ssid === ssid &&
        active.bssid === bssid

    const isBlockingMode =
        mode === "editing" || mode === "confirm-delete"
    const isDisabled =
        isBlockingMode && !isActive

    const isHovered =
        hover.type === "bssid" &&
        hover.ssid === ssid &&
        hover.bssid === bssid

    return (
        <div
            className={styles.row}
            data-selected={isActive || undefined}
            data-hovered={isHovered || undefined}
            data-disabled={isDisabled || undefined}
            onClick={() => {
                if (isDisabled) return

                setActive({
                    type: "bssid",
                    ssid,
                    bssid
                })
            }}
            onMouseEnter={() =>
                hoverWhitelist({
                    type: "bssid",
                    ssid,
                    bssid
                })
            }
            onMouseLeave={() => hoverWhitelist(null)}
        >
            <div className={styles.indent} />
            <div className={styles.indent} />

            <div className={styles.icon}>📡</div>

            <div className={styles.chevron} />

            <div className={styles.label} title={bssid}>
                {bssid}
            </div>

            <div className={styles.actions}>
                <button className={styles.btn}>🗑</button>
            </div>
        </div>
    )
}