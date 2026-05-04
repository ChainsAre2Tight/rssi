import { loadWhitelist } from "../../features/whitelist/loadWhitelist"
import { removeWhitelistBSSID } from "../../services/apiWhitelist"
import { useAppStore } from "../../store/useAppStore"
import { IRail, TRail } from "./Rail"
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
    const setActiveForce = useAppStore(s => s.setWhitelistActiveForce)
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

    async function confirmDelete() {
        const measurementId = useAppStore.getState().context.measurementId
        if (!measurementId) return

        try {
            // optional: optimistic UI lock
            useAppStore.getState().setWhitelistLoading(true)

            await removeWhitelistBSSID(
                measurementId,
                ssid,
                bssid,
                false,
            )

            const fresh = await loadWhitelist(measurementId)

            useAppStore.getState().setWhitelist(
                measurementId,
                fresh
            )

        } catch (err) {
            console.error("Failed to delete BSSID", err)
        } finally {
            // UI reset is handled by setWhitelist reconciliation
            useAppStore.getState().setWhitelistLoading(false)
        }
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
                    bssid,
                    sensor: null,
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
                    bssid,
                    sensor: null,
                })
            }
            onMouseLeave={() => hoverWhitelist(null)}
        >
            <IRail />
            <TRail />

            <div className={styles.label} title={bssid}>
                {bssid}
            </div>

            <div className={styles.actions}>
                {isConfirmDelete ? (
                    <>
                        <button
                            className={`${styles.btn} ${styles.btnConfirm}`}
                            onClick={(e) => {
                                e.stopPropagation()
                                cancelDelete()
                            }}
                        >
                            ✕
                        </button>

                        <button
                            className={`${styles.btn} ${styles.btnDanger}`}
                            onClick={(e) => {
                                e.stopPropagation()
                                confirmDelete()
                            }}
                        >
                            🗑
                        </button>
                    </>
                ) : (
                    <button
                        className={styles.btn}
                        onClick={(e) => {
                            e.stopPropagation()

                            setActiveForce({
                                type: "bssid",
                                ssid,
                                bssid,
                                sensor: null,
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
