import type { Incident, Modality, Measurement, Importance, Whitelist } from "./general"
import type { LocalizationData, Sensor } from "../services/localizationApi"

type WhitelistUIType =
    | "ssid"
    | "bssid"
    | "sensor"
    | "sensor-desc"
    | "sensor-pos"
    | "add-ssid"
    | "add-bssid"
    | "measurement-name"
    | "measurement-description"
    | "measurement-detection"
    | "measurement-csi"
    | "measurement-localization"
    | null

export interface AppState {
    context: {
        measurementId: number | null
        mode: "active" | "report"
    }

    measurements: {
        items: Measurement[]
        loading: boolean
        loaded: boolean
    }

    active: {
        running: boolean
        offsetS: number
    }

    report: {
        startTimeUs: number | null
        endTimeUs: number | null

        incidentsByModality: Record<Modality, Incident[]>

        loading: boolean
        loaded: boolean
    }

    whitelist: {
        byMeasurement: Record<number, Whitelist>
        loading: boolean
        loaded: boolean
    }

    timeline: {
        global: {
            zoom: number
            scrollX: number
        }
        incident: {
            zoom: number
            scrollX: number
        }
    }

    selection: {
        incidentId: string | null
        warningKey: string | null // something like incidentId + ":" + warning.signal .. althoug on different metadata might collide
    }

    filters: {
        severities: Record<Importance, boolean>
        query: string
    }

    hover: {
        incidentId: string | null
        warningKey: string | null
        timelineTimeUs: number | null

        whitelist: {
            type: "ssid" | "bssid" | "sensor" | null
            ssid: string | null
            bssid: string | null
            sensor: string | null
        }
    }

    layout: {
        explorerWidth: number
        globalTimelineHeight: number
        warningTimelineHeight: number
        warningListWidth: number
        whitelistWidth: number
    }

    whitelistUI: {
        active: {
            type: WhitelistUIType
            ssid: string | null
            bssid: string | null
            sensor: string | null
        }

        mode: "idle" | "editing" | "confirm-delete"

        draftValue: string

        lastAction: {
            type: "add" | "rename" | null
            ssid?: string
            bssid?: string
        } | null

        measurementDraft: {
            name: string
            description: string
        } | null

        sensorDraft: {
            description: string
            x: string
            y: string
            z: string
        } | null
    }

    localization: {
        mode: "timeline" | "map" | "whitelist"
        cache: Record<string, LocalizationData>
        sensors: Record<string, Sensor[]>
        loading: Record<string, boolean>
        error: Record<string, string | null>
    }

    // actions
    setMeasurements: (items: Measurement[]) => void
    setMeasurementsLoading: (loading: boolean) => void

    setMeasurement: (id: number | null) => void
    setMode: (mode: "active" | "report") => void

    setActiveRunning: (running: boolean) => void
    setActiveOffset: (offset: number) => void

    setReport: (
        incidentsByModality: Record<Modality, Incident[]>,
        start: number,
        end: number
    ) => void
    setReportLoading: (loading: boolean) => void

    selectIncident: (id: string | null) => void
    selectWarning: (key: string | null) => void

    hoverIncident: (id: string | null) => void
    hoverWarning: (key: string | null) => void
    setTimelineCursor: (timeUs: number | null) => void

    setLayout: (
        update:
            | Partial<AppState["layout"]>
            | ((prev: AppState["layout"]) => AppState["layout"])
    ) => void

    toggleImportance: (importance: Importance) => void

    setLocalizationMode: (mode: "timeline" | "map" | "whitelist") => void
    setLocalizationData: (incidentKey: string, data: LocalizationData) => void
    setSensors: (measurementId: number, sensors: Sensor[]) => void
    setLocalizationLoading: (incidentKey: string, loading: boolean) => void
    setLocalizationError: (incidentKey: string, error: string | null) => void
    clearLocalizationCache: () => void

    setSearchQuery: (query: string) => void

    setWhitelistLoading: (loading: boolean) => void
    setWhitelist: (
        measurementId: number,
        whitelist: Whitelist,
    ) => void
    clearWhitelist: () => void

    setWhitelistActive: (payload: AppState["whitelistUI"]["active"]) => void
    setWhitelistActiveForce: (payload: AppState["whitelistUI"]["active"]) => void
    setWhitelistMode: (mode: AppState["whitelistUI"]["mode"]) => void
    setWhitelistDraft: (value: string) => void
    clearWhitelistUI: () => void
    setWhitelistLastAction: (action: AppState["whitelistUI"]["lastAction"]) => void
    reconcileWhitelistUI: (whitelist: Whitelist) => void
    hoverWhitelist: (
        payload: AppState["hover"]["whitelist"] | null
    ) => void

    updateMeasurement: (measurement: Measurement) => void
    getCurrentMeasurement: () => Measurement | null
    setMeasurementDraft: (draft: { name: string; description: string } | null) => void
    setSensorDraft: (
        draft: {
            description: string
            x: string
            y: string
            z: string
        } | null
    ) => void
}