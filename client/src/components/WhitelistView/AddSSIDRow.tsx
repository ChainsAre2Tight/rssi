import { useAppStore } from "../../store/useAppStore"
import styles from "./WhitelistView.module.css"

export function AddSSIDRow() {
    const active = useAppStore(s => s.whitelistUI.active)
    const setActive = useAppStore(s => s.setWhitelistActive)
    const mode = useAppStore(s => s.whitelistUI.mode)
    const draft = useAppStore(s => s.whitelistUI.draftValue)
    const setDraft = useAppStore(s => s.setWhitelistDraft)
    const setMode = useAppStore(s => s.setWhitelistMode)
    const clearUI = useAppStore(s => s.clearWhitelistUI)

    const isActive = active.type === "add-ssid"
    const isBlockingMode =
        mode === "editing" || mode === "confirm-delete"
    const isDisabled =
        isBlockingMode && !isActive
    
    const isEditing =
        mode === "editing" &&
        active.type === "add-ssid"
    
    function submit() {
        if (!draft.trim()) {
            clearUI()
            return
        }

        console.log("ADD SSID", draft)

        clearUI()
    }

    function cancel() {
        clearUI()
    }

    return (
        <div
            className={`${styles.row} ${styles.addRow}`}
            data-selected={isActive || undefined}
            data-disabled={isDisabled || undefined}
            data-editing={isEditing || undefined}
            onClick={() => {
                if (isDisabled) return

                setActive({
                    type: "add-ssid",
                    ssid: null,
                    bssid: null
                })

                setDraft("")
                setMode("editing")
            }}
        >
            <div className={styles.indent} />
            <div className={styles.icon} />
            <div className={styles.chevron} />

            <div className={styles.label}>
                {isEditing ? (
                    <input
                        className={styles.input}
                        value={draft}
                        autoFocus
                        placeholder="New SSID"
                        onChange={e => setDraft(e.target.value)}
                        onClick={e => e.stopPropagation()}
                        onKeyDown={(e) => {
                            if (e.key === "Enter") submit()
                            if (e.key === "Escape") cancel()
                        }}
                    />
                ) : (
                    "+ Add SSID"
                )}
            </div>

            {isEditing && (
                <div className={styles.actions}>
                    <button
                        className={styles.btn}
                        onClick={(e) => {
                            e.stopPropagation()
                            submit()
                        }}
                    >
                        ✔
                    </button>

                    <button
                        className={styles.btn}
                        onClick={(e) => {
                            e.stopPropagation()
                            cancel()
                        }}
                    >
                        ✕
                    </button>
                </div>
            )}
        </div>
    )
}