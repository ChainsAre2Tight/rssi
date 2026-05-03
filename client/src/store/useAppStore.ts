import { create } from "zustand"
import { persist } from "zustand/middleware"

import type { AppState } from "../types/state"
import type { Importance } from "../types/general"

const defaultLayout = {
    explorerWidth: 300,
    globalTimelineHeight: 300,
    warningTimelineHeight: 400,
    warningListWidth: 300,
}

export const useAppStore = create<AppState>()(
persist(
(set, get) => ({

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

    whitelist: {
        byMeasurement: {},
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
            whitelist: true,
        },
        query: "",
    },

    hover: {
        incidentId: null,
        warningKey: null,
        timelineTimeUs: null,
        whitelist: {
            type: null,
            ssid: null,
            bssid: null,
        },
    },

    layout: defaultLayout,

    whitelistUI: {
        active: {
            type: null,
            ssid: null,
            bssid: null
        },
        mode: "idle",
        draftValue: "",
        lastAction: null,
        measurementDraft: null,
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
    
    toggleImportance: (importance: Importance) =>
        set((state) => ({
            filters: {
                ...state.filters,
                severities: {
                    ...state.filters.severities,
                    [importance]: !state.filters.severities[importance]
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
    
    setSearchQuery: (query: string) =>
        set((state) => ({
            filters: {
                ...state.filters,
                query,
            }
        })),
    
    setWhitelistLoading: (loading) =>
        set((state) => ({
            whitelist: {
                ...state.whitelist,
                loading
            }
        })),

    setWhitelist: (measurementId, whitelist) =>
        set((state) => {
            const newWhitelistState = {
                byMeasurement: {
                    ...state.whitelist.byMeasurement,
                    [measurementId]: whitelist
                },
                loading: false,
                loaded: true
            }

            // --- reconcile ---
            const { active } = state.whitelistUI

            let stillExists = false

            if (active.type === "ssid") {
                stillExists = !!whitelist[active.ssid ?? ""]
            }

            if (active.type === "bssid") {
                const ssid = active.ssid ?? ""
                const bssid = active.bssid ?? ""

                stillExists =
                    !!whitelist[ssid] &&
                    !!whitelist[ssid][bssid]
            }

            if (active.type === "add-ssid" || active.type === "add-bssid") {
                stillExists = false
            }

            return {
                whitelist: newWhitelistState,
                whitelistUI: {
                    ...state.whitelistUI,
                    active: stillExists
                        ? active
                        : {
                            type: null,
                            ssid: null,
                            bssid: null
                        },
                    mode: "idle",
                    draftValue: "",
                    measurementDraft: null,
                }
            }
        }),

    clearWhitelist: () =>
        set({
            whitelist: {
                byMeasurement: {},
                loading: false,
                loaded: false
            }
        }),
    
    setWhitelistActive: (payload) =>
        set((state) => {
            const isSame =
                state.whitelistUI.active.type === payload.type &&
                state.whitelistUI.active.ssid === payload.ssid &&
                state.whitelistUI.active.bssid === payload.bssid

            if (isSame) {
                return {
                    whitelistUI: {
                        ...state.whitelistUI,
                        active: {
                            type: null,
                            ssid: null,
                            bssid: null
                        },
                        mode: "idle",
                        draftValue: ""
                    }
                }
            }

            return {
                whitelistUI: {
                    ...state.whitelistUI,
                    active: payload,
                    mode: "idle",
                    draftValue: ""
                }
            }
        }),
    setWhitelistActiveForce: (payload) =>
        set((state) => ({
            whitelistUI: {
                ...state.whitelistUI,
                active: payload
            }
        })),
    setWhitelistMode: (mode) =>
        set((state) => ({
            whitelistUI: {
                ...state.whitelistUI,
                mode
            }
        })),
    setWhitelistDraft: (value) =>
        set((state) => ({
            whitelistUI: {
                ...state.whitelistUI,
                draftValue: value
            }
        })),
    clearWhitelistUI: () =>
        set((state) => ({
            whitelistUI: {
                ...state.whitelistUI,
                active: {
                    type: null,
                    ssid: null,
                    bssid: null
                },
                mode: "idle",
                draftValue: "",
                measurementDraft: null,
            }
        })),
    setWhitelistLastAction: (action) =>
        set((state) => ({
            whitelistUI: {
                ...state.whitelistUI,
                lastAction: action
            }
        })),
    hoverWhitelist: (payload) =>
        set((state) => ({
            hover: {
                ...state.hover,
                whitelist: payload ?? {
                    type: null,
                    ssid: null,
                    bssid: null
                }
            }
        })),
    reconcileWhitelistUI: (whitelist) =>
        set((state) => {
            const { active } = state.whitelistUI

            if (!active.type) {
                return {
                    whitelistUI: {
                        ...state.whitelistUI,
                        mode: "idle",
                        draftValue: ""
                    }
                }
            }

            // Validate existence
            let stillExists = false

            if (active.type === "ssid") {
                stillExists = !!whitelist[active.ssid ?? ""]
            }

            if (active.type === "bssid") {
                const ssid = active.ssid ?? ""
                const bssid = active.bssid ?? ""

                stillExists =
                    !!whitelist[ssid] &&
                    !!whitelist[ssid][bssid]
            }

            // add rows are always cleared after reload
            if (active.type === "add-ssid" || active.type === "add-bssid") {
                stillExists = false
            }

            return {
                whitelistUI: {
                    ...state.whitelistUI,
                    active: stillExists
                        ? active
                        : {
                            type: null,
                            ssid: null,
                            bssid: null
                        },
                    mode: "idle",
                    draftValue: "",
                    measurementDraft: null,
                }
            }
        }),
    
    updateMeasurement: (updated) =>
        set((state) => ({
            measurements: {
                ...state.measurements,
                items: state.measurements.items.map(m =>
                    m.id === updated.id ? updated : m
                )
            }
        })),
    
    getCurrentMeasurement: () => {
        const state = get()
        const id = state.context.measurementId
        if (!id) return null

        return state.measurements.items.find(m => m.id === id) ?? null
    },

    setMeasurementDraft: (draft) =>
        set((state) => ({
            whitelistUI: {
                ...state.whitelistUI,
                measurementDraft: draft
            }
        })),
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
        },

        whitelist: {
            byMeasurement: state.whitelist.byMeasurement,
        },
    }),

    onRehydrateStorage: () => (state) => {

        if (!state) return

        if (state.report.startTimeUs !== null) {
            state.report.loaded = true
        }

    }
}
))