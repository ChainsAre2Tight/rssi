import type { Severity } from "../types/general"

export interface TimelineTrack {
    id: string
    label?: string
    height: number

    lastExpandedHeight?: number

    collapsible?: boolean
    resizable?: boolean
}

export interface TimelineItem {
    id: string
    start: number
    end: number
    severity: Severity
}

export interface TrackLayoutItem {
    id: string
    y: number
    height: number

    contentY: number
    contentHeight: number

    laneHeight: number
    laneCount: number

    track: TimelineTrack
}

export interface Viewport {
    start: number
    end: number
}