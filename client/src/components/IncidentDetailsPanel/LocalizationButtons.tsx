import { useAppStore } from "../../store/useAppStore"
import { fetchLocalization, requestLocalization } from "../../services/localizationApi"
import styles from "./LocalizationButtons.module.css"

export default function LocalizationButtons() {
    const incidentId = useAppStore(s => s.selection.incidentId)
    const incidentsByModality = useAppStore(s => s.report.incidentsByModality)
    const measurementId = useAppStore(s => s.context.measurementId)
    const startTimeUs = useAppStore(s => s.report.startTimeUs)
    const endTimeUs = useAppStore(s => s.report.endTimeUs)

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

            // After sending, fetch current status
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

    return (
        <div className={styles.root}>
            <button
                className={styles.button}
                onClick={handleRequestLocation}
                disabled={isLoading}
                title="Fetch existing localization data"
            >
                {isLoading ? "Loading..." : "Request Location"}
            </button>

            <button
                className={styles.button}
                onClick={handleSendForLocalization}
                disabled={isLoading}
                title="Enqueue new localization jobs"
            >
                {isLoading ? "Processing..." : "Send for Localization"}
            </button>

            {hasData && (
                <button
                    className={styles.button}
                    onClick={handleRequestLocation}
                    disabled={isLoading}
                    title="Refresh localization data"
                >
                    {isLoading ? "Loading..." : "Refresh"}
                </button>
            )}

            {isError && (
                <div className={styles.error}>
                    {isError}
                </div>
            )}
        </div>
    )
}
