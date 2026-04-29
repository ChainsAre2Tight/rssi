import { useEffect, useState } from "react"
import styles from "./LocalizationButtons.module.css"

import { useAppStore } from "../../store/useAppStore"
import { isWhitelisted } from "../../features/whitelist/utils"
import { addWhitelistPair, removeWhitelistPair } from "../../services/apiWhitelist"
import { reloadWhitelist } from "../../features/whitelist/reloadWhitelist"

export default function WhitelistButtons() {

    const incidentId = useAppStore(s => s.selection.incidentId)
    const incidentsByModality = useAppStore(s => s.report.incidentsByModality)
    const measurementId = useAppStore(s => s.context.measurementId)

    const whitelist = useAppStore(s =>
        measurementId !== null
            ? s.whitelist.byMeasurement[measurementId]
            : undefined
    )

    const incident = Object.values(incidentsByModality)
        .flat()
        .find(i => i.id === incidentId)

    const [status, setStatus] = useState<{
        state: "Added" | "Removed" | "Ignored" | "Processing"
        message?: string
    } | null>(null)

    useEffect(() => {
        if (!status) return
        const t = setTimeout(() => setStatus(null), 500)
        return () => clearTimeout(t)
    }, [status])

    useEffect(() => {
        setStatus(null)
    }, [incidentId])

    if (!incident || !measurementId || !incident.identity) return null

    const ssid = incident.identity.ssid
    const bssid = incident.identity.bssid

    const isWhiteliste = isWhitelisted(whitelist, ssid, bssid)
    const label = isWhiteliste ? "Remove from whitelist" : "Add to whitelist"

    async function handleToggle() {
        if (!measurementId) return

        setStatus({ state: "Processing" })

        try {
            let res = isWhiteliste
                ? await removeWhitelistPair(measurementId, ssid, bssid)
                : await addWhitelistPair(measurementId, ssid, bssid)
            

            if (res.status === "ok") {
                setStatus({
                    state: isWhiteliste ? "Removed" : "Added"
                })
            } else {
                setStatus({ state: "Ignored", message: res.action })
            }

            reloadWhitelist(measurementId)

        } catch (e) {
            setStatus({
                state: "Ignored",
                message: "request failed"
            })
        }
    }

    return (
        <div className={styles.root}>

            <button
                className={styles.button}
                onClick={handleToggle}
                disabled={status?.state === "Processing"}
            >
                {status?.state === "Processing"
                    ? "Processing..."
                    : status?.state
                        ? `${status.state}`
                        : label}
            </button>

            {status?.state === "Ignored" && (
                <div className={styles.error}>
                    {status.message ?? "ignored"}
                </div>
            )}

        </div>
    )
}
