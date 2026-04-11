export interface TimelineTrack {
    id: string
    label?: string
    height: number

    collapsible?: boolean
    collapsed?: boolean
    resizable?: boolean
}

export type TrackLayout = {
    id: string
    y: number
    height: number
}