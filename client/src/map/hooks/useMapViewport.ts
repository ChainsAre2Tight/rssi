import { useState } from "react"
import type { SpatialViewport, SpatialBounds } from "../types"
import { fitBounds } from "../utils/geometry"

export function useMapViewport(initial?: SpatialViewport | SpatialBounds) {
    const [viewport, setViewport] = useState<SpatialViewport>(() => {
        if (!initial) {
            return { minX: 0, maxX: 10, minY: 0, maxY: 10 }
        }

        // If it's already a viewport, use it
        if ("minX" in initial && "maxX" in initial) {
            return initial as SpatialViewport
        }

        // If it's bounds, fit with padding
        return fitBounds(initial as SpatialBounds, 0.15)
    })

    const width = viewport.maxX - viewport.minX
    const height = viewport.maxY - viewport.minY

    return {
        viewport,
        setViewport,
        width,
        height,
    }
}
