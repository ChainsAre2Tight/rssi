import type { Sensor } from "../../services/localizationApi"
import { useAppStore } from "../../store/useAppStore"
import { IRail, TRail } from "./Rail"
import styles from "./WhitelistView.module.css"

export function SensorDescriptionRow({
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
        active.type === "sensor-desc" &&
        active.sensor === sensor.name

    function startEdit() {

        setActiveForce({
            type: "sensor-desc",
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

        console.log("PATCH SENSOR DESCRIPTION", sensor.name, draft.description)

        clearUI()
    }

    return (
        <div
            className={styles.row}
            onClick={(e) => {
                e.stopPropagation()
                setActive({
                    type: "sensor-desc",
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
            <TRail />

            <div className={styles.description}>
                {isEditing ? (
                    <textarea
                        className={styles.textarea}
                        value={draft?.description ?? ""}
                        onChange={e =>
                            setDraft({ ...draft!, description: e.target.value })
                        }
                    />
                ) : (
                    <span title={sensor.description}>{sensor.description || "No description"}</span>
                )}
            </div>

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
