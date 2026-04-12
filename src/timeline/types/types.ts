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
    trackId: string
    start: number
    end: number

    laneIndex: number
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
