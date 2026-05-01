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

    const setMode = useAppStore(s => s.setWhitelistMode)
    const clearUI = useAppStore(s => s.clearWhitelistUI)

    const isConfirmDelete =
        mode === "confirm-delete" &&
        active.type === "bssid" &&
        active.ssid === ssid &&
        active.bssid === bssid

    function confirmDelete() {
        console.log("DELETE BSSID", ssid, bssid)

        // simulate refetch
        clearUI()
    }

    function cancelDelete() {
        clearUI()
    }

    const isDisabled =
        isBlockingMode && !match.isPrimary

    return (
        <div
            className={styles.row}
            data-selected={match.isPrimary || undefined}
            data-secondary={match.isSecondary || undefined}
            data-disabled={isDisabled || undefined}
            data-confirm={isConfirmDelete || undefined}
            onClick={() => {
                if (isDisabled) return

                setActive({
                    type: "bssid",
                    ssid,
                    bssid
                })
            }}
            onKeyDown={(e) => {
                if (!match.isPrimary) return
                if (mode === "confirm-delete") {
                    if (e.key === "Enter") confirmDelete()
                    if (e.key === "Escape") cancelDelete()
                }
            }}
            tabIndex={0}
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
                {isConfirmDelete ? (
                    <>
                        <button
                            className={styles.btn}
                            onClick={(e) => {
                                e.stopPropagation()
                                confirmDelete()
                            }}
                        >
                            ✔
                        </button>

                        <button
                            className={styles.btn}
                            onClick={(e) => {
                                e.stopPropagation()
                                cancelDelete()
                            }}
                        >
                            ✕
                        </button>
                    </>
                ) : (
                    <button
                        className={styles.btn}
                        onClick={(e) => {
                            e.stopPropagation()

                            setActive({
                                type: "bssid",
                                ssid,
                                bssid
                            })

                            setMode("confirm-delete")
                        }}
                    >
                        🗑
                    </button>
                )}
            </div>
        </div>
    )
}