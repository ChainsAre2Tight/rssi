export interface TimelineTrack {
    id: string
    label?: string
    height: number

    lastExpandedHeight?: number

    collapsible?: boolean
    resizable?: boolean
}
