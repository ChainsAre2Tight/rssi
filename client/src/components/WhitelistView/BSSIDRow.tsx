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

    const isBlockingMode =
        mode === "editing" || mode === "confirm-delete"

    const match = (() => {
        const isPrimary =
            (active.type === "bssid" &&
                active.ssid === ssid &&
                active.bssid === bssid) ||
            (hover.type === "bssid" &&
                hover.ssid === ssid &&
                hover.bssid === bssid)

        const isSecondary =
            (active.type === "bssid" &&
                active.bssid === bssid &&
                active.ssid !== ssid) ||
            (hover.type === "bssid" &&
                hover.bssid === bssid &&
                hover.ssid !== ssid)

        return { isPrimary, isSecondary }
    })()

    const isDisabled =
        isBlockingMode && !match.isPrimary

    return (
        <div
            className={styles.row}
            data-selected={match.isPrimary || undefined}
            data-secondary={match.isSecondary || undefined}
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