import { create } from "zustand"


import type { AppState } from "../types/state"


const defaultLayout = {
    explorerWidth: 300,
    globalTimelineHeight: 300,
    warningTimelineHeight: 400
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
        warningKey: null
    },

    hover: {
        incidentId: null,
        warningKey: null,
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
            },
            loaded: false
        },

        selection: {
            incidentId: null,
            warningKey: null
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
                warningKey: null
            }
        })),

    selectWarning: (key) =>
        set((state) => ({
            selection: {
                ...state.selection,
                warningKey: key
            }
        })),

    hoverIncident: (id) =>
        set((state) => ({
            hover: {
                ...state.hover,
                incidentId: id
            }
        })),

    hoverWarning: (key) =>
        set((state) => ({
            hover: {
                ...state.hover,
                warningKey: key
            }
        })),

    setTimelineCursor: (timeUs) =>
        set((state) => ({
            hover: {
                ...state.hover,
                timelineTimeUs: timeUs
            }
    })),

    setLayout: (update) =>
        set((state) => ({
            layout:
                typeof update === "function"
                    ? update(state.layout)
                    : { ...state.layout, ...update }
        }))
    }))
