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

    trackId: string

    severity?: string
    data?: Record<string, unknown>
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

export interface HitTestResult {
    item: TimelineItem
    trackId: string
    laneIndex: number
}

export interface Viewport {
    start: number
    end: number
}
