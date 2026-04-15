import { useAppStore } from "../../store/useAppStore"
import { fetchLocalization, requestLocalization } from "../../services/localizationApi"
import styles from "./LocalizationButtons.module.css"
import { useEffect, useState } from "react"

export default function LocalizationButtons() {
    const incidentId = useAppStore(s => s.selection.incidentId)
    const incidentsByModality = useAppStore(s => s.report.incidentsByModality)
    const measurementId = useAppStore(s => s.context.measurementId)
    const startTimeUs = useAppStore(s => s.report.startTimeUs)
    const endTimeUs = useAppStore(s => s.report.endTimeUs)

    const setLocalizationMode = useAppStore(s => s.setLocalizationMode)

    const { cache, loading, error } = useAppStore(s => s.localization)
    const { setLocalizationData, setLocalizationLoading, setLocalizationError } = useAppStore()

    const incident = Object.values(incidentsByModality)
        .flat()
        .find(i => i.id === incidentId)

    if (!incident || !measurementId || !startTimeUs || !endTimeUs || incidentId === null) {
        return null
    }

    const isLoading = loading[incidentId] || false
    const isError = error[incidentId] || null
    const hasData = cache[incidentId] || null

    const [jobSummary, setJobSummary] = useState<{
        created: number
        ignored: number
    } | null>(null)

    useEffect(() => {
        if (!jobSummary) return

        const t = setTimeout(() => setJobSummary(null), 10_000)
        return () => clearTimeout(t)
    }, [jobSummary])

    useEffect(() => {
        setJobSummary(null)
    }, [incidentId])

    async function handleRequestLocation() {
        if (!incidentId || !measurementId
            || !startTimeUs || !endTimeUs
            || !incident || !incident.identity) return

        setLocalizationLoading(incidentId, true)
        setLocalizationError(incidentId, null)

        try {
            const data = await fetchLocalization({
                measurementId,
                startTimeUs,
                endTimeUs,
                bssid: incident.identity.bssid,
                modality: incident.modality,
            })

            setLocalizationData(incidentId, data)
            setLocalizationMode("map")
        } catch (err) {
            const message = err instanceof Error ? err.message : "Failed to fetch localization"
            setLocalizationError(incidentId, message)
        }
    }

    async function handleSendForLocalization() {
        if (!incidentId || !measurementId
            || !startTimeUs || !endTimeUs
            || !incident || !incident.identity) return

        setLocalizationLoading(incidentId, true)
        setLocalizationError(incidentId, null)

        try {
            const result = await requestLocalization({
                measurementId,
                startTimeUs,
                endTimeUs,
                bssid: incident.identity.bssid,
                modality: incident.modality,
            })

            setJobSummary({
                created: result.jobs_created,
                ignored: result.jobs_ignored,
            })

            // Switch to map view
            setLocalizationMode("map")

            // Fetch latest data
            const data = await fetchLocalization({
                measurementId,
                startTimeUs,
                endTimeUs,
                bssid: incident.identity.bssid,
                modality: incident.modality,
            })

            setLocalizationData(incidentId, data)

        } catch (err) {
            const message = err instanceof Error ? err.message : "Failed to request localization"
            setLocalizationError(incidentId, message)
        }
    }
    const primaryLabel = hasData ? "Refresh" : "Request Location"
    const primaryTitle = hasData
        ? "Refresh localization data"
        : "Fetch existing localization data"

    return (
        <div className={styles.root}>

            <button
                className={styles.button}
                onClick={handleRequestLocation}
                disabled={isLoading}
                title={primaryTitle}
            >
                {isLoading ? "Loading..." : primaryLabel}
            </button>

            <button
                className={styles.button}
                onClick={handleSendForLocalization}
                disabled={isLoading}
                title={
                    jobSummary
                        ? `Created: ${jobSummary.created}, Ignored: ${jobSummary.ignored}`
                        : "Enqueue new localization jobs"
                }
            >
                {isLoading
                    ? "Processing..."
                    : jobSummary
                        ? `+${jobSummary.created} / ${jobSummary.ignored} ignored`
                        : "Send for Localization"}
            </button>

            {isError && (
                <div className={styles.error}>
                    {isError}
                </div>
            )}
        </div>
    )
}
