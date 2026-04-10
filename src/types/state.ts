import type { Incident, Modality, Measurement } from "./general"


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
        warningType: string | null
    }

    hover: {
        incidentId: string | null
        warningType: string | null
        timelineTimeUs: number | null
    }

    layout: {
        explorerWidth: number
        timelineHeight: number
        detailsHeight: number
    }

    ui: {
        warningPanelExpanded: Record<string, boolean>
    }

    // actions
    setMeasurements: (items: Measurement[]) => void
    setMeasurementsLoading: (loading: boolean) => void

    setMeasurement: (id: number | null) => void
    setMode: (mode: "active" | "report") => void

    setReport: (
        incidentsByModality: Record<Modality, Incident[]>,
        start: number,
        end: number
    ) => void
    setReportLoading: (loading: boolean) => void

    selectIncident: (id: string | null) => void
    selectWarning: (type: string | null) => void

    hoverIncident: (id: string | null) => void
    hoverWarning: (type: string | null) => void
    setTimelineCursor: (timeUs: number | null) => void
}