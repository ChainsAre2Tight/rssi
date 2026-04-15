import type { Severity } from "../types/general"

export interface TimelineTrack {
    id: string
    label?: string
    height: number

    lastExpandedHeight?: number

    collapsible?: boolean
    resizable?: boolean

    scrollY?: number
}

export type TimelineEventType = "incident" | "warning"

export interface TimelineItem {
    id: string

    type: TimelineEventType
    key: string // for external sync

    start: number
    end: number
    severity: Severity

    laneIndex?: number
}

export interface TrackLayoutItem {
    id: string
    y: number
    height: number

    contentY: number
    contentHeight: number
    viewportHeight: number

    laneHeight: number
    laneCount: number

    scrollY: number

    track: TimelineTrack
}

export interface Viewport {
    start: number
    end: number
}

export type TimelineLanes = TimelineItem[][]

export interface TimelineAdapterResult {
    itemsByTrack: Record<string, TimelineLanes>

    // IMPORTANT for future sync
    index: {
        byKey: Map<string, TimelineItem>
        byId: Map<string, TimelineItem>
    }

    bounds: {
        start: number
        end: number
    }

    trackIds: string[]
    hasItems: boolean
}