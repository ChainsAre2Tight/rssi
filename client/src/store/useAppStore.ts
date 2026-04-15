import { create } from "zustand"
import { persist } from "zustand/middleware"

import type { AppState } from "../types/state"
import type { Severity } from "../types/general"

const defaultLayout = {
    explorerWidth: 300,
    globalTimelineHeight: 300,
    warningTimelineHeight: 400,
    warningListWidth: 300,
}

export const useAppStore = create<AppState>()(
persist(
(set) => ({

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

    filters: {
        severities: {
            critical: true,
            high: true,
            medium: true,
            low: true,
            info: true,
        }
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

    localization: {
        mode: "timeline",
        cache: {},
        sensors: {},
        loading: {},
        error: {},
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
            },
            localization: {
                mode: "timeline",
                cache: {},
                sensors: {},
                loading: {},
                error: {},
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
        })),
    
    toggleSeverity: (severity: Severity) =>
        set((state) => ({
            filters: {
                ...state.filters,
                severities: {
                    ...state.filters.severities,
                    [severity]: !state.filters.severities[severity]
                }
            }
        })),

    setLocalizationMode: (mode) =>
        set((state) => ({
            localization: {
                ...state.localization,
                mode,
            }
        })),

    setLocalizationData: (incidentKey, data) =>
        set((state) => {
            const newCache = { ...state.localization.cache, [incidentKey]: data }

            // Enforce max cache size (keep 5 most recent)
            const MAX_CACHE_SIZE = 5
            if (Object.keys(newCache).length > MAX_CACHE_SIZE) {
                const keys = Object.keys(newCache)
                const toRemove = keys[0]
                delete newCache[toRemove]
            }

            return {
                localization: {
                    ...state.localization,
                    cache: newCache,
                    loading: { ...state.localization.loading, [incidentKey]: false },
                    error: { ...state.localization.error, [incidentKey]: null },
                }
            }
        }),

    setSensors: (measurementId, sensors) =>
        set((state) => ({
            localization: {
                ...state.localization,
                sensors: {
                    ...state.localization.sensors,
                    [String(measurementId)]: sensors,
                }
            }
        })),

    setLocalizationLoading: (incidentKey, loading) =>
        set((state) => ({
            localization: {
                ...state.localization,
                loading: {
                    ...state.localization.loading,
                    [incidentKey]: loading,
                }
            }
        })),

    setLocalizationError: (incidentKey, error) =>
        set((state) => ({
            localization: {
                ...state.localization,
                error: {
                    ...state.localization.error,
                    [incidentKey]: error,
                }
            }
        })),

    clearLocalizationCache: () =>
        set({
            localization: {
                mode: "timeline",
                cache: {},
                sensors: {},
                loading: {},
                error: {},
            }
        }),

}),
{
    name: "app-store",

    version: 1,

    partialize: (state) => ({
        context: {
            measurementId: state.context.measurementId,
            mode: state.context.mode
        },

        layout: state.layout,

        active: {
            offsetS: state.active.offsetS
        },

        report: {
            startTimeUs: state.report.startTimeUs,
            endTimeUs: state.report.endTimeUs,
            incidentsByModality: state.report.incidentsByModality
        }
    }),

    onRehydrateStorage: () => (state) => {

        if (!state) return

        if (state.report.startTimeUs !== null) {
            state.report.loaded = true
        }

    }
}
))