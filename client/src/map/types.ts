import type { Sensor } from "../services/localizationApi"

export interface SpatialViewport {
    minX: number
    maxX: number
    minY: number
    maxY: number
}

export interface SpatialBounds {
    minX: number
    maxX: number
    minY: number
    maxY: number
}

export interface Point {
    x: number
    y: number
    z: number
    timeUs: number
}

export type SegmentGapType = "solid" | "dashed"

export interface TrajectorySegment {
    points: Point[]
    startTimeUs: number
    endTimeUs: number
    style: {
        gapType: SegmentGapType
        calibrated: boolean
    }
}

export interface MapAdapterResult {
    segments: TrajectorySegment[]
    sensors: Sensor[]
    bounds: SpatialBounds
}

export interface CursorInterpolation {
    position: { x: number; y: number; z: number } | null
    segmentIndex: number | null
}
