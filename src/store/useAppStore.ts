import { create } from "zustand"


import type { AppState } from "../types/state"


const defaultLayout = {
    explorerWidth: 300,
    timelineHeight: 300,
    detailsHeight: 400
}

export const useAppStore = create<AppState>((set) => ({
    context: {
        measurementId: null,
        mode: "report"
    },

    measurements: {
        items: [],
        loading: false,
        loaded: false
    },

    active: {
        running: false,
        offsetS: 300
    },

    report: {
        startTimeUs: null,
        endTimeUs: null,

        incidentsByModality: {
            logical: [],
            physical: [],
        },

        loading: false,
        loaded: false
    },

    timeline: {
        global: {
            zoom: 1,
            scrollX: 0
        },
        incident: {
            zoom: 1,
            scrollX: 0
        }
    },

    selection: {
        incidentId: null,
        warningType: null
    },

    hover: {
        incidentId: null,
        warningType: null,
        timelineTimeUs: null
    },

    layout: defaultLayout,

    ui: {
        warningPanelExpanded: {}
    },

    // ACTIONS
    setMeasurementsLoading: (loading) =>
        set((state) => ({
            measurements: {
                ...state.measurements,
                loading
            }
        })),

    setMeasurements: (items) =>
        set({
            measurements: {
                items,
                loading: false,
                loaded: true
            }
        }),

    setMeasurement: (id) =>
        set((state) => ({
        context: {
            ...state.context,
            measurementId: id
        },

        active: {
            ...state.active,
            running: false
        },

        report: {
            ...state.report,
            incidentsByModality: {
                logical: [],
                physical: [],
                ml: []
            },
            loaded: false
        },

        selection: {
            incidentId: null,
            warningType: null
        }
        })),
    
    // TODO: probably stop polling on mode change? we'll see
    setMode: (mode) =>
        set((state) => ({
        context: {
            ...state.context,
            mode
        }
        })),
    
    setActiveRunning: (running) =>
        set((state) => ({
            active: {
                ...state.active,
                running
            }
        })),

    setActiveOffset: (offset) =>
        set((state) => ({
            active: {
                ...state.active,
                offsetS: offset
            }
        })),

    setReportLoading: (loading) =>
        set((state) => ({
        report: {
            ...state.report,
            loading
        }
        })),

    setReport: (incidentsByModality, start, end) =>
        set({
            report: {
                startTimeUs: start,
                endTimeUs: end,
                incidentsByModality,
                loading: false,
                loaded: true
            }
        }),

    selectIncident: (id) =>
        set((state) => ({
            selection: {
                ...state.selection,
                incidentId: id,
                warningType: null
            }
        })),

    selectWarning: (type) =>
        set((state) => ({
            selection: {
                ...state.selection,
                warningType: type
            }
        })),

    hoverIncident: (id) =>
        set((state) => ({
            hover: {
                ...state.hover,
                incidentId: id
            }
        })),

    hoverWarning: (type) =>
        set((state) => ({
            hover: {
                ...state.hover,
                warningType: type
            }
        })),

    setTimelineCursor: (timeUs) =>
        set((state) => ({
            hover: {
                ...state.hover,
                timelineTimeUs: timeUs
            }
    }))
}))