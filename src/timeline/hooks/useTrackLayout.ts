import type { TimelineTrack, TrackLayout } from "../types/types"

const COLLAPSED_HEIGHT = 28

export function useTrackLayout(tracks: TimelineTrack[]): TrackLayout[] {
    let y = 0

    return tracks.map(track => {
        const height = track.collapsed
            ? COLLAPSED_HEIGHT
            : track.height

        const layout: TrackLayout = {
            id: track.id,
            y,
            height,
        }

        y += height

        return layout
    })
}
