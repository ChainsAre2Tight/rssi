import { fetchSensors, type Sensor } from "../../services/localizationApi"
import { patchSensorPosition } from "../../services/sensorApi"
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

    const measurementId = useAppStore.getState().context.measurementId
    const setSensors = useAppStore((s) => s.setSensors)

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

    async function submit() {
        if (!draft) return
        
        const valueX = parseFloat(draft.x.trim())
        const valueY = parseFloat(draft.y.trim())
        const valueZ = parseFloat(draft.z.trim())

        if (!valueX || !valueY || !valueZ || (
            valueX === sensor.x && valueY === sensor.y && valueZ === sensor.z
        )) {
            clearUI()
            return
        }

        const response = await patchSensorPosition({
            measurementId: measurementId!,
            device: sensor.name,
            x: valueX,
            y: valueY,
            z: valueZ,
        })

        if (response && response.status && response.status == "ok") {
            const sensors = await fetchSensors(measurementId!)
            setSensors(measurementId!, sensors)
        }

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
                        onClick={(e) => {e.stopPropagation()}}
                    />
                    <input className={`${styles.input} ${styles.inputShort}`}
                        value={draft!.y}
                        onChange={e => setDraft({ ...draft!, y: e.target.value })}
                        onClick={(e) => {e.stopPropagation()}}
                    />
                    <input className={`${styles.input} ${styles.inputShort}`}
                        value={draft!.z}
                        onChange={e => setDraft({ ...draft!, z: e.target.value })}
                        onClick={(e) => {e.stopPropagation()}}
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
