import type { SpatialViewport } from "../types"

export interface SpatialMapper {
    scale: number
    offsetX: number
    offsetY: number

    toCanvas: (x: number, y: number) => { x: number; y: number }
    toWorld: (x: number, y: number) => { x: number; y: number }
}

export function createSpatialMapper(
    viewport: SpatialViewport,
    canvasWidth: number,
    canvasHeight: number
): SpatialMapper {
    const viewportWidth = viewport.maxX - viewport.minX
    const viewportHeight = viewport.maxY - viewport.minY

    if (viewportWidth === 0 || viewportHeight === 0) {
        return {
            scale: 1,
            offsetX: 0,
            offsetY: 0,
            toCanvas: (x, y) => ({ x, y }),
            toWorld: (x, y) => ({ x, y }),
        }
    }

    // Uniform scale (fixes distortion)
    const scaleX = canvasWidth / viewportWidth
    const scaleY = canvasHeight / viewportHeight
    const scale = Math.min(scaleX, scaleY)

    // Rendered world size in pixels
    const renderWidth = viewportWidth * scale
    const renderHeight = viewportHeight * scale

    // Centering offsets (letterboxing)
    const offsetX = (canvasWidth - renderWidth) / 2
    const offsetY = (canvasHeight - renderHeight) / 2

    function toCanvas(worldX: number, worldY: number) {
        const x = offsetX + (worldX - viewport.minX) * scale
        const y =
            canvasHeight -
            (offsetY + (worldY - viewport.minY) * scale)

        return { x, y }
    }

    function toWorld(canvasX: number, canvasY: number) {
        const x = viewport.minX + (canvasX - offsetX) / scale
        const y =
            viewport.minY +
            (canvasHeight - canvasY - offsetY) / scale

        return { x, y }
    }

    return {
        scale,
        offsetX,
        offsetY,
        toCanvas,
        toWorld,
    }
}
