import type { SpatialBounds, SpatialViewport } from "../types"

export function fitBounds(
    bounds: SpatialBounds,
    padding: number = 0.1
): SpatialViewport {
    const width = bounds.maxX - bounds.minX
    const height = bounds.maxY - bounds.minY

    const paddingX = width * padding
    const paddingY = height * padding

    return {
        minX: bounds.minX - paddingX,
        maxX: bounds.maxX + paddingX,
        minY: bounds.minY - paddingY,
        maxY: bounds.maxY + paddingY,
    }
}

export function getViewportBounds(
    points: Array<{ x: number; y: number; z?: number }>
): SpatialBounds {
    if (points.length === 0) {
        return { minX: 0, maxX: 1, minY: 0, maxY: 1 }
    }

    let minX = Infinity
    let maxX = -Infinity
    let minY = Infinity
    let maxY = -Infinity

    for (const p of points) {
        minX = Math.min(minX, p.x)
        maxX = Math.max(maxX, p.x)
        minY = Math.min(minY, p.y)
        maxY = Math.max(maxY, p.y)
    }

    // Ensure non-zero bounds
    if (minX === maxX) {
        minX -= 0.5
        maxX += 0.5
    }
    if (minY === maxY) {
        minY -= 0.5
        maxY += 0.5
    }

    return { minX, maxX, minY, maxY }
}

/**
 * Convert world coordinates to canvas coordinates
 */
export function worldToCanvas(
    worldX: number,
    worldY: number,
    viewport: SpatialViewport,
    canvasWidth: number,
    canvasHeight: number
): { x: number; y: number } {
    const viewportWidth = viewport.maxX - viewport.minX
    const viewportHeight = viewport.maxY - viewport.minY

    const x = ((worldX - viewport.minX) / viewportWidth) * canvasWidth
    const y = canvasHeight - ((worldY - viewport.minY) / viewportHeight) * canvasHeight

    return { x, y }
}

/**
 * Convert canvas coordinates to world coordinates
 */
export function canvasToWorld(
    canvasX: number,
    canvasY: number,
    viewport: SpatialViewport,
    canvasWidth: number,
    canvasHeight: number
): { x: number; y: number } {
    const viewportWidth = viewport.maxX - viewport.minX
    const viewportHeight = viewport.maxY - viewport.minY

    const x = viewport.minX + (canvasX / canvasWidth) * viewportWidth
    const y = viewport.maxY - (canvasY / canvasHeight) * viewportHeight

    return { x, y }
}

/**
 * Zoom viewport around an anchor point (cursor-centered)
 */
export function zoomViewport(
    viewport: SpatialViewport,
    zoomFactor: number,
    anchorX?: number,
    anchorY?: number
): SpatialViewport {
    // Default to center if no anchor provided
    const centerX = anchorX ?? (viewport.minX + viewport.maxX) / 2
    const centerY = anchorY ?? (viewport.minY + viewport.maxY) / 2

    const width = viewport.maxX - viewport.minX
    const height = viewport.maxY - viewport.minY

    const newWidth = width * zoomFactor
    const newHeight = height * zoomFactor

    // Scale around the anchor point
    const anchorRelX = (centerX - viewport.minX) / width
    const anchorRelY = (centerY - viewport.minY) / height

    const newMinX = centerX - newWidth * anchorRelX
    const newMaxX = centerX + newWidth * (1 - anchorRelX)
    const newMinY = centerY - newHeight * anchorRelY
    const newMaxY = centerY + newHeight * (1 - anchorRelY)

    return {
        minX: newMinX,
        maxX: newMaxX,
        minY: newMinY,
        maxY: newMaxY,
    }
}

/**
 * Pan viewport by world distance
 */
export function panViewport(
    viewport: SpatialViewport,
    deltaWorldX: number,
    deltaWorldY: number
): SpatialViewport {
    return {
        minX: viewport.minX - deltaWorldX,
        maxX: viewport.maxX - deltaWorldX,
        minY: viewport.minY - deltaWorldY,
        maxY: viewport.maxY - deltaWorldY,
    }
}
