import { useRef } from "react"
import type { TrackLayoutItem } from "../utils/trackLayout"
import type { TimelineTrack } from "../types/types"

interface Params {
    layout: TrackLayoutItem[]
    tracks: TimelineTrack[]
    setTracks: React.Dispatch<React.SetStateAction<TimelineTrack[]>>
}

const HEADER_HEIGHT = 28

export function useTrackResizing({
    layout,
    tracks,
    setTracks,
}: Params) {
    const isResizing = useRef(false)
    const activeTrackId = useRef<string | null>(null)
    const startY = useRef(0)
    const startHeight = useRef(0)

    function findSeparator(y: number): TrackLayoutItem | null {
        for (let i = 0; i < layout.length; i++) {
            const t = layout[i]

            const sepTop = t.y + t.height - 6
            const sepBottom = t.y + t.height

            if (y >= sepTop && y <= sepBottom) {
                return t
            }
        }
        return null
    }

    function onMouseDown(e: React.MouseEvent) {
        const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
        const y = e.clientY - rect.top

        const target = findSeparator(y)
        if (!target) return

        e.preventDefault()

        isResizing.current = true
        activeTrackId.current = target.id
        startY.current = e.clientY

        const track = tracks.find(t => t.id === target.id)
        if (!track) return

        startHeight.current =
            track.height <= HEADER_HEIGHT
                ? track.lastExpandedHeight ?? 120
                : track.height
    }

    function onMouseMove(e: React.MouseEvent) {
        const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
        const y = e.clientY - rect.top

        const target = findSeparator(y)

        if (target || isResizing.current) {
            ;(e.currentTarget as HTMLElement).style.cursor = "row-resize"
        } else {
            ;(e.currentTarget as HTMLElement).style.cursor = "default"
        }

        if (!isResizing.current || !activeTrackId.current) return

        const delta = e.clientY - startY.current

        setTracks(prev =>
            prev.map(t => {
                if (t.id !== activeTrackId.current) return t

                let newHeight = startHeight.current + delta

                if (newHeight <= HEADER_HEIGHT) {
                    return {
                        ...t,
                        lastExpandedHeight:
                            t.height > HEADER_HEIGHT
                                ? t.height
                                : t.lastExpandedHeight,
                        height: HEADER_HEIGHT,
                    }
                }

                return {
                    ...t,
                    height: newHeight,
                }
            })
        )
    }

    function onMouseUp() {
        isResizing.current = false
        activeTrackId.current = null
    }

    function onMouseLeave() {
        isResizing.current = false
        activeTrackId.current = null
    }

    return {
        bind: {
            onMouseDown,
            onMouseMove,
            onMouseUp,
            onMouseLeave,
        },
    }
}
