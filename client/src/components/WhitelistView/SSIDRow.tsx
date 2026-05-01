import { loadWhitelist } from "../../features/whitelist/loadWhitelist"
import { removeWhitelistSSID, renameWhitelistSSID } from "../../services/apiWhitelist"
import { useAppStore } from "../../store/useAppStore"
import { TRail } from "./Rail"
import styles from "./WhitelistView.module.css"

export function SSIDRow({ ssid }: { ssid: string }) {
    const active = useAppStore(s => s.whitelistUI.active)
    const mode = useAppStore(s => s.whitelistUI.mode)
    const hover = useAppStore(s => s.hover.whitelist)

    const setActive = useAppStore(s => s.setWhitelistActive)
    const setActiveForce = useAppStore(s => s.setWhitelistActiveForce)
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
    
    const isEditing =
        mode === "editing" &&
        active.type === "ssid" &&
        active.ssid === ssid
    
    const draft = useAppStore(s => s.whitelistUI.draftValue)
    const setDraft = useAppStore(s => s.setWhitelistDraft)
    const setMode = useAppStore(s => s.setWhitelistMode)
    const clearUI = useAppStore(s => s.clearWhitelistUI)
    const isConfirmDelete =
        mode === "confirm-delete" &&
        active.type === "ssid" &&
        active.ssid === ssid

    async function confirmDelete() {
        const { context, setWhitelistLoading, setWhitelist } = useAppStore.getState()
        const measurementId = context.measurementId
        if (!measurementId) return

        try {
            setWhitelistLoading(true)

            await removeWhitelistSSID(
                measurementId,
                ssid
            )

            const fresh = await loadWhitelist(measurementId)

            setWhitelist(measurementId, fresh)
        } catch (err) {
            console.error("DELETE SSID failed", err)
        } finally {
            setWhitelistLoading(false)
        }
    }

    function cancelDelete() {
        clearUI()
    }

    async function submitRename() {
        const value = draft.trim()

        if (!value || value === ssid) {
            clearUI()
            return
        }

        const { context, setWhitelistLoading, setWhitelist } = useAppStore.getState()
        const measurementId = context.measurementId
        if (!measurementId) return

        try {
            setWhitelistLoading(true)

            await renameWhitelistSSID(
                measurementId,
                ssid,
                value
            )

            const fresh = await loadWhitelist(measurementId)

            setWhitelist(measurementId, fresh)
        } catch (err) {
            console.error("RENAME SSID failed", err)
        } finally {
            setWhitelistLoading(false)
        }
    }

    function cancel() {
        clearUI()
    }

    return (
        <div
            className={styles.row}
            data-selected={isActive || undefined}
            data-hovered={isHovered || undefined}
            data-disabled={isDisabled || undefined}
            data-editing={isEditing || undefined}
            data-confirm={isConfirmDelete || undefined}
            onClick={() => {
                if (isDisabled) return

                setActive({
                    type: "ssid",
                    ssid,
                    bssid: null
                })
            }}
            onKeyDown={(e) => {
                if (!isActive) return

                if (mode === "confirm-delete") {
                    if (e.key === "Enter") confirmDelete()
                    if (e.key === "Escape") cancelDelete()
                }

                if (mode === "editing") {
                    if (e.key === "Enter") submitRename()
                    if (e.key === "Escape") cancel()
                }
            }}
            tabIndex={0}
            onMouseEnter={() =>
                hoverWhitelist({
                    type: "ssid",
                    ssid,
                    bssid: null
                })
            }
            onMouseLeave={() => hoverWhitelist(null)}
        >
            <TRail />

            <div className={styles.icon}>🖧</div>

            <div className={styles.label}>
                {isEditing ? (
                    <input
                        className={styles.input}
                        value={draft}
                        autoFocus
                        onChange={e => setDraft(e.target.value)}
                        onClick={e => e.stopPropagation()}
                        onKeyDown={(e) => {
                            if (e.key === "Enter") {
                                submitRename()
                            }
                            if (e.key === "Escape") {
                                cancel()
                            }
                        }}
                    />
                ) : (
                    <span title={ssid}>{ssid}</span>
                )}
            </div>

            <div className={styles.actions}>
                {isEditing ? (
                    <>
                        <button className={`${styles.btn} ${styles.btnConfirm}`} onClick={(e) => { e.stopPropagation(); submitRename() }}>
                            ✔
                        </button>
                        <button className={`${styles.btn} ${styles.btnDanger}`} onClick={(e) => { e.stopPropagation(); cancel() }}>
                            ✕
                        </button>
                    </>
                ) : isConfirmDelete ? (
                    <>
                        <button
                            className={`${styles.btn} ${styles.btnDanger}`}
                            onClick={(e) => {
                                e.stopPropagation()
                                confirmDelete()
                            }}
                        >
                            🗑
                        </button>

                        <button
                            className={`${styles.btn} ${styles.btnConfirm}`}
                            onClick={(e) => {
                                e.stopPropagation()
                                cancelDelete()
                            }}
                        >
                            ✕
                        </button>
                    </>
                ) : (
                    <>
                        <button
                            className={styles.btn}
                            onClick={(e) => {
                                e.stopPropagation()
                                setActiveForce({ type: "ssid", ssid, bssid: null })
                                setDraft(ssid)
                                setMode("editing")
                            }}
                        >
                            ✎
                        </button>

                        <button
                            className={styles.btn}
                            onClick={(e) => {
                                e.stopPropagation()

                                setActiveForce({ type: "ssid", ssid, bssid: null })
                                setMode("confirm-delete")
                            }}
                        >
                            🗑
                        </button>
                    </>
                )}
            </div>
        </div>
    )
}
