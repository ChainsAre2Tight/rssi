import type { Sensor } from "../../services/localizationApi"
import { useAppStore } from "../../store/useAppStore"
import { IRail, LRail } from "./Rail"
import styles from "./WhitelistView.module.css"

export function SensorPositionRow({
    sensor,
    isHovered,
    isSelected,
}: {
    sensor: Sensor,
    isHovered: boolean,
    isSelected: boolean,
}) {
    const active = useAppStore(s => s.whitelistUI.active)
    const mode = useAppStore(s => s.whitelistUI.mode)
    const setActive = useAppStore(s => s.setWhitelistActive)
    const hoverWhitelist = useAppStore(s => s.hoverWhitelist)

    const draft = useAppStore(s => s.whitelistUI.sensorDraft)
    const setDraft = useAppStore(s => s.setSensorDraft)
    const setActiveForce = useAppStore(s => s.setWhitelistActiveForce)
    const setMode = useAppStore(s => s.setWhitelistMode)
    const clearUI = useAppStore(s => s.clearWhitelistUI)

    const isEditing =
        mode === "editing" &&
        active.type === "sensor-pos" &&
        active.sensor === sensor.name

    function startEdit() {
        setActiveForce({
            type: "sensor-pos",
            sensor: sensor.name,
            ssid: null,
            bssid: null,
        })

        setDraft({
            description: sensor.description,
            x: String(sensor.x),
            y: String(sensor.y),
            z: String(sensor.z),
        })

        setMode("editing")
    }

    function submit() {
        if (!draft) return

        console.log("PATCH SENSOR POSITION", sensor.name, draft)

        clearUI()
    }

    return (
        <div
            className={styles.row}
            onClick={(e) => {
                e.stopPropagation()
                setActive({
                    type: "sensor-pos",
                    sensor: sensor.name,
                    ssid: null,
                    bssid: null,
                })
            }}
            onMouseEnter={() =>
                hoverWhitelist({
                    type: "sensor",
                    sensor: sensor.name,
                    ssid: null,
                    bssid: null,
                })
            }
            data-hovered={isHovered}
            data-selected={isSelected}
            onMouseLeave={() => hoverWhitelist(null)}
        >
            <IRail />
            <LRail />

            {isEditing ? (
                <>
                    <input className={`${styles.input} ${styles.inputShort}`}
                        value={draft!.x}
                        onChange={e => setDraft({ ...draft!, x: e.target.value })}
                    />
                    <input className={`${styles.input} ${styles.inputShort}`}
                        value={draft!.y}
                        onChange={e => setDraft({ ...draft!, y: e.target.value })}
                    />
                    <input className={`${styles.input} ${styles.inputShort}`}
                        value={draft!.z}
                        onChange={e => setDraft({ ...draft!, z: e.target.value })}
                    />
                </>
            ) : (
                <>
                    <span>X: {sensor.x}</span>
                    <span>Y: {sensor.y}</span>
                    <span>Z: {sensor.z}</span>
                </>
            )}

            <div className={styles.actions}>
                {isEditing ? (
                    <>
                        <button
                            className={`${styles.btn} ${styles.btnConfirm}`}
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
                                clearUI()
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
                            startEdit()
                        }}
                    >
                        ✎
                    </button>
                )}
            </div>
        </div>
    )
}
