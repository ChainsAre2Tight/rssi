import { patchMeasurement } from "../../services/measurements"
import { useAppStore } from "../../store/useAppStore"
import styles from "./WhitelistView.module.css"

export function MeasurementHeader() {
    const measurement = useAppStore(s => s.getCurrentMeasurement())

    const active = useAppStore(s => s.whitelistUI.active)
    const mode = useAppStore(s => s.whitelistUI.mode)
    const draft = useAppStore(s => s.whitelistUI.measurementDraft)

    const setActive = useAppStore(s => s.setWhitelistActive)
    const setActiveForce = useAppStore(s => s.setWhitelistActiveForce)
    const setMode = useAppStore(s => s.setWhitelistMode)
    const setMeasurementDraft = useAppStore(s => s.setMeasurementDraft)
    const clearUI = useAppStore(s => s.clearWhitelistUI)

    if (!measurement) return <div>No measurement selected</div>

    const isBlockingMode =
        mode === "editing" || mode === "confirm-delete"

    // NAME
    const isNameActive = active.type === "measurement-name"
    const isNameEditing = isNameActive && mode === "editing"
    const isNameDisabled = isBlockingMode && !isNameActive

    // DESCRIPTION
    const isDescActive = active.type === "measurement-description"
    const isDescEditing = isDescActive && mode === "editing"
    const isDescDisabled = isBlockingMode && !isDescActive

    function startEditName() {
        setActiveForce({ type: "measurement-name", ssid: null, bssid: null })
        setMeasurementDraft({
            name: measurement!.name,
            description: measurement!.description
        })
        setMode("editing")
    }

    function startEditDescription() {
        setActiveForce({ type: "measurement-description", ssid: null, bssid: null })
        setMeasurementDraft({
            name: measurement!.name,
            description: measurement!.description
        })
        setMode("editing")
    }

    async function submitName() {
        if (!draft) return

        const value = draft.name.trim()

        if (!value || value === measurement!.name) {
            clearUI()
            return
        }

        try {
            const res = await patchMeasurement({
                measurement_id: measurement!.id,
                name: value
            })

            if ("measurement" in res) {
                console.log(123, res.measurement)
                useAppStore.getState().updateMeasurement(res.measurement)
            }

        } catch (err) {
            console.error("PATCH NAME failed", err)
        } finally {
            clearUI()
        }
    }

    async function submitDescription() {
        if (!draft) return

        const value = draft.description.trim()

        if (!value || value === measurement!.description) {
            clearUI()
            return
        }

        try {
            const res = await patchMeasurement({
                measurement_id: measurement!.id,
                description: value,
            })

            if ("measurement" in res) {
                useAppStore.getState().updateMeasurement(res.measurement)
            }

        } catch (err) {
            console.error("PATCH DESCRIPTION failed", err)
        } finally {
            clearUI()
        }
    }

    function cancel() {
        clearUI()
    }

    return (
        <div
            className={styles.row}
            data-selected={(isNameActive || isDescActive) || undefined}
        >
            {/* NAME */}
            <div
                className={styles.headerGroup}
                data-disabled={isNameDisabled || undefined}
                onClick={() => {
                    if (isNameDisabled) return
                    setActive({ type: "measurement-name", ssid: null, bssid: null })
                }}
            >
                <div className={styles.label}>
                    {isNameEditing ? (
                        <input
                            className={styles.input}
                            autoFocus
                            value={draft?.name ?? ""}
                            onChange={e =>
                                setMeasurementDraft({
                                    ...(draft ?? { name: "", description: "" }),
                                    name: e.target.value
                                })
                            }
                            onClick={e => e.stopPropagation()}
                            onKeyDown={(e) => {
                                if (e.key === "Enter") submitName()
                                if (e.key === "Escape") cancel()
                            }}
                        />
                    ) : (
                        <span>Name: {measurement.name}</span>
                    )}
                </div>

                <div className={styles.actions}>
                    {isNameEditing ? (
                        <>
                            <button className={`${styles.btn} ${styles.btnConfirm}`} onClick={(e) => { e.stopPropagation(); submitName() }}>
                                ✔
                            </button>
                            <button className={`${styles.btn} ${styles.btnDanger}`} onClick={(e) => { e.stopPropagation(); cancel() }}>
                                ✕
                            </button>
                        </>
                    ) : (
                        <button className={styles.btn} onClick={(e) => { e.stopPropagation(); startEditName() }}>
                            ✎
                        </button>
                    )}
                </div>
            </div>

            <div className={styles.separator}></div>

            {/* DESCRIPTION */}
            <div
                className={styles.headerGroup}
                data-disabled={isDescDisabled || undefined}
                onClick={() => {
                    if (isDescDisabled) return
                    setActive({ type: "measurement-description", ssid: null, bssid: null })
                }}
            >
                <div className={styles.description}>
                    {isDescEditing ? (
                        <textarea
                            className={styles.textarea}
                            value={draft?.description ?? ""}
                            onChange={e =>
                                setMeasurementDraft({
                                    ...(draft ?? { name: "", description: "" }),
                                    description: e.target.value
                                })
                            }
                            onClick={e => e.stopPropagation()}
                            onKeyDown={(e) => {
                                if (e.key === "Escape") cancel()
                                if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
                                    submitDescription()
                                }
                            }}
                        />
                    ) : (
                        <span>Description: {measurement.description}</span>
                    )}
                </div>

                <div className={styles.actions}>
                    {isDescEditing ? (
                        <>
                            <button className={`${styles.btn} ${styles.btnConfirm}`} onClick={(e) => { e.stopPropagation(); submitDescription() }}>
                                ✔
                            </button>
                            <button className={`${styles.btn} ${styles.btnDanger}`} onClick={(e) => { e.stopPropagation(); cancel() }}>
                                ✕
                            </button>
                        </>
                    ) : (
                        <button className={styles.btn} onClick={(e) => { e.stopPropagation(); startEditDescription() }}>
                            ✎
                        </button>
                    )}
                </div>
            </div>

            {/* RIGHT SIDE */}
            <div className={styles.headerRight}>
                <button
                    className={styles.btn}
                    onClick={(e) => {
                        e.stopPropagation()
                        console.log("RERUN DETECTORS", measurement.id)
                    }}
                >
                    Rerun detectors
                </button>
            </div>
        </div>
    )
}
