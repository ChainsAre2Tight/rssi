import type { Incident, Modality, Measurement, Severity } from "./general"


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
        severities: Record<Severity, boolean>
    }

    hover: {
        incidentId: string | null
        warningKey: string | null
        timelineTimeUs: number | null
    }

    layout: {
        explorerWidth: number
        globalTimelineHeight: number
        warningTimelineHeight: number
        warningListWidth: number
    }

    ui: {
        warningPanelExpanded: Record<string, boolean>
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

    toggleSeverity: (severity: Severity) => void
}