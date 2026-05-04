import type { Sensor } from "../../services/localizationApi"
import { useAppStore } from "../../store/useAppStore"
import { TRail } from "./Rail"
import styles from "./WhitelistView.module.css"

export function SensorRow({
    sensor,
}: {
    sensor: Sensor,
}) {
    const active = useAppStore(s => s.whitelistUI.active)
    const mode = useAppStore(s => s.whitelistUI.mode)
    const hover = useAppStore(s => s.hover.whitelist)

    const setActive = useAppStore(s => s.setWhitelistActive)
    const setActiveForce = useAppStore(s => s.setWhitelistActiveForce)
    const hoverWhitelist = useAppStore(s => s.hoverWhitelist)

    const isActive =
        active.type === "sensor" &&
        active.sensor === sensor.name

    const isBlockingMode =
        mode === "editing" || mode === "confirm-delete"
    const isDisabled =
        isBlockingMode && !isActive

    const isHovered =
        hover.type === "sensor" &&
        hover.sensor === sensor.name
    
    const isEditing =
        mode === "editing" &&
        active.type === "sensor" &&
        active.sensor === sensor.name
    
    const draft = useAppStore(s => s.whitelistUI.positionDraft)
    const setDraft = useAppStore(s => s.setPositionDraft)
    const setMode = useAppStore(s => s.setWhitelistMode)
    const clearUI = useAppStore(s => s.clearWhitelistUI)

    async function submitPositions() {
        if (!draft) return
        const x = draft.x.trim()
        const y = draft.x.trim()
        const z = draft.x.trim()

        if (!x || !y || !z) {
            clearUI()
            return
        }

        console.log(`UPDATE SENSOR ${sensor.name} to x: ${x}; y: ${y}; z: ${z}`)

        clearUI()
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
            onClick={() => {
                if (isDisabled) return

                setActive({
                    type: "sensor",
                    ssid: null,
                    bssid: null,
                    sensor: sensor.name,
                })
            }}
            onKeyDown={(e) => {
                if (!isActive) return

                if (mode === "editing") {
                    if (e.key === "Enter") submitPositions()
                    if (e.key === "Escape") cancel()
                }
            }}
            tabIndex={0}
            onMouseEnter={() =>
                hoverWhitelist({
                    type: "sensor",
                    ssid: null,
                    bssid: null,
                    sensor: sensor.name,
                })
            }
            onMouseLeave={() => hoverWhitelist(null)}
        >
            <TRail />

            <div className={styles.icon}>📡</div>

            <div className={styles.label}>
                <span title={sensor.name}>{sensor.name}</span>
            </div>

            {isEditing ? (
                <>
                    <input
                        className={`${styles.input} ${styles.inputShort}`}
                        value={draft!.x}
                        autoFocus
                        onChange={e => setDraft({
                            x: e.target.value,
                            y: draft!.y,
                            z: draft!.z
                        })}
                        onClick={e => e.stopPropagation()}
                    />
                    <input
                        className={`${styles.input} ${styles.inputShort}`}
                        value={draft!.y}
                        autoFocus
                        onChange={e => setDraft({
                            x: draft!.x,
                            y: e.target.value,
                            z: draft!.z
                        })}
                        onClick={e => e.stopPropagation()}
                    />
                    <input
                        className={`${styles.input} ${styles.inputShort}`}
                        value={draft!.z}
                        autoFocus
                        onChange={e => setDraft({
                            x: draft!.x,
                            z: e.target.value,
                            y: draft!.y
                        })}
                        onClick={e => e.stopPropagation()}
                    />
                </>
            ) : (
                <>
                    <div className={styles.label}>
                        <span title={String(sensor.x)}>X: {sensor.x}</span>
                    </div>
                    <div className={styles.label}>
                        <span title={String(sensor.y)}>Y: {sensor.y}</span>
                    </div>
                    <div className={styles.label}>
                        <span title={String(sensor.z)}>Z: {sensor.z}</span>
                    </div>
                </>
            )}
            

            <div className={styles.actions}>
                {isEditing ? (
                    <>
                        <button className={`${styles.btn} ${styles.btnConfirm}`} onClick={(e) => { e.stopPropagation(); submitPositions() }}>
                            ✔
                        </button>
                        <button className={`${styles.btn} ${styles.btnDanger}`} onClick={(e) => { e.stopPropagation(); cancel() }}>
                            ✕
                        </button>
                    </>
                ) : (
                    <button
                        className={styles.btn}
                        onClick={(e) => {
                            e.stopPropagation()
                            setActiveForce({ type: "sensor", ssid: null, bssid: null, sensor: sensor.name })
                            setDraft({
                                x: String(sensor.x),
                                y: String(sensor.y),
                                z: String(sensor.z),
                            })
                            setMode("editing")
                        }}
                    >
                        ✎
                    </button>
                )}
            </div>
        </div>
    )
}