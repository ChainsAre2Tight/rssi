import { loadWhitelist } from "../../features/whitelist/loadWhitelist"
import { addWhitelistPair } from "../../services/apiWhitelist"
import { useAppStore } from "../../store/useAppStore"
import { IRail, LRail } from "./Rail"
import styles from "./WhitelistView.module.css"

const MAX_BSSID_LENGTH = 17

function getBssidState(value: string) {
    const v = value.toUpperCase()

    if (v.length === 0) return "empty"

    if (v.length > MAX_BSSID_LENGTH) return "invalid"

    // Only allow hex + colon
    if (!/^[0-9A-F:]*$/.test(v)) return "invalid"

    const parts = v.split(":")

    for (let i = 0; i < parts.length; i++) {
        const part = parts[i]

        // each block max 2 chars
        if (part.length > 2) return "invalid"

        // all but last block must be exactly 2 if colon exists
        if (i < parts.length - 1 && part.length !== 2) return "invalid"
    }

    // full valid check
    if (parts.length === 6 && parts.every(p => p.length === 2)) {
        return "valid"
    }

    return "partial"
}

export function AddBSSIDRow({ ssid }: { ssid: string }) {
    const active = useAppStore(s => s.whitelistUI.active)
    const setActive = useAppStore(s => s.setWhitelistActive)
    const mode = useAppStore(s => s.whitelistUI.mode)
    const draft = useAppStore(s => s.whitelistUI.draftValue)
    const setDraft = useAppStore(s => s.setWhitelistDraft)
    const setMode = useAppStore(s => s.setWhitelistMode)
    const clearUI = useAppStore(s => s.clearWhitelistUI)

    const isActive =
        active.type === "add-bssid" &&
        active.ssid === ssid

    const isBlockingMode =
        mode === "editing" || mode === "confirm-delete"

    const isDisabled =
        isBlockingMode && !isActive

    const isEditing =
        mode === "editing" &&
        active.type === "add-bssid" &&
        active.ssid === ssid

    const state = getBssidState(draft)
    const isValid = state === "valid"

    async function submit() {
        if (!isValid) return

        const { context, setWhitelistLoading, setWhitelist } = useAppStore.getState()
        const measurementId = context.measurementId
        if (!measurementId) return

        try {
            setWhitelistLoading(true)

            await addWhitelistPair(
                measurementId,
                ssid,
                draft
            )

            const fresh = await loadWhitelist(measurementId)

            setWhitelist(measurementId, fresh)
        } catch (err) {
            console.error("ADD BSSID failed", err)
        } finally {
            setWhitelistLoading(false)
        }
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
                    type: "add-bssid",
                    ssid,
                    bssid: null
                })

                setDraft("")
                setMode("editing")
            }}
        >
            <IRail />
            <LRail />

            <div className={styles.label}>
                {isEditing ? (
                    <input
                        className={styles.input}
                        data-invalid={state === "invalid" || undefined}
                        data-valid={state === "valid" || undefined}
                        value={draft}
                        autoFocus
                        placeholder="AA:BB:CC:DD:EE:FF"
                        maxLength={MAX_BSSID_LENGTH}
                        onChange={(e) => {
                            setDraft(e.target.value.toUpperCase())
                        }}
                        onPaste={(e) => {
                            const text = e.clipboardData.getData("text")
                            if (text.length > MAX_BSSID_LENGTH) {
                                e.preventDefault()
                            }
                        }}
                        onClick={(e) => e.stopPropagation()}
                        onKeyDown={(e) => {
                            if (e.key === "Enter") {
                                if (isValid) submit()
                            }
                            if (e.key === "Escape") {
                                cancel()
                            }
                        }}
                        onBlur={() => {
                            // optional UX choice:
                            // keep open OR auto-cancel invalid
                            if (!isValid) return
                            submit()
                        }}
                    />
                ) : (
                    "+ Add BSSID"
                )}
            </div>

            {isEditing && (
                <div className={styles.actions}>
                    <button
                        className={`${styles.btn} ${styles.btnConfirm}`}
                        disabled={!isValid}
                        onClick={(e) => {
                            e.stopPropagation()
                            submit()
                        }}
                    >
                        ✔
                    </button>

                    <button
                        className={`${styles.btn} ${styles.btnDanger}`}
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
