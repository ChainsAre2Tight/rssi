import type { LocalizationResult, Sensor } from "../../services/localizationApi"
import type { TrajectorySegment, MapAdapterResult, SpatialBounds } from "../types"
import { getViewportBounds } from "../utils/geometry"

const WINDOW_STEP_US = 30_000_000 // 30 seconds (from backend config)
const SMALL_GAP_US = WINDOW_STEP_US // gap <= step: same segment
const LARGE_GAP_US = 2 * WINDOW_STEP_US // gap > 2*step: break segment

/**
 * Build segments from localization results
 * Segments are split by:
 * 1. Time continuity (small/medium/large gaps)
 * 2. Calibration state changes
 */
export function buildLocalizationAdapter(params: {
    locations: LocalizationResult[]
    sensors: Sensor[]
}): MapAdapterResult {
    const { locations, sensors } = params

    // Sort by start time
    const sorted = [...locations].sort((a, b) => a.start_time_us - b.start_time_us)

    if (sorted.length === 0) {
        const emptyBounds: SpatialBounds = { minX: 0, maxX: 10, minY: 0, maxY: 10 }
        return {
            segments: [],
            sensors,
            bounds: emptyBounds,
        }
    }

    const segments = buildSegments(sorted)
    const allPoints = sorted.map(loc => ({
        x: loc.estimated_position[0],
        y: loc.estimated_position[1],
        z: loc.estimated_position[2],
    }))
    const sensorPoints = sensors.map(s => ({ x: s.x, y: s.y }))
    const bounds = getViewportBounds([...allPoints, ...sensorPoints])

    return {
        segments,
        sensors,
        bounds,
    }
}

/**
 * Build trajectory segments with gap and calibration detection
 */
function buildSegments(sorted: LocalizationResult[]): TrajectorySegment[] {
    if (sorted.length === 0) return []

    const segments: TrajectorySegment[] = []
    let currentSegmentStart = 0
    let lastCalibrated = sorted[0].metadata?.calibrated ?? false

    for (let i = 1; i < sorted.length; i++) {
        const prev = sorted[i - 1]
        const curr = sorted[i]

        const gap = curr.start_time_us - prev.end_time_us
        const calibrationChanged = (curr.metadata?.calibrated ?? false) !== lastCalibrated

        // Check if we should break segment
        if (gap > LARGE_GAP_US || calibrationChanged) {
            // Flush current segment
            const segment = createSegment(
                sorted.slice(currentSegmentStart, i),
                lastCalibrated
            )
            if (segment) {
                segments.push(segment)
            }

            currentSegmentStart = i
            lastCalibrated = curr.metadata?.calibrated ?? false
        }
    }

    // Flush final segment
    const finalSegment = createSegment(
        sorted.slice(currentSegmentStart),
        lastCalibrated
    )
    if (finalSegment) {
        segments.push(finalSegment)
    }

    return segments
}

/**
 * Create a single trajectory segment with appropriate gap styling
 */
function createSegment(
    results: LocalizationResult[],
    calibrated: boolean
): TrajectorySegment | null {
    if (results.length === 0) return null

    const points = results.map(loc => ({
        x: loc.estimated_position[0],
        y: loc.estimated_position[1],
        z: loc.estimated_position[2],
        timeUs: loc.start_time_us,
    }))

    const gapType = detectGapType(results)

    return {
        points,
        startTimeUs: results[0].start_time_us,
        endTimeUs: results[results.length - 1].end_time_us,
        style: {
            gapType,
            calibrated,
        },
    }
}

/**
 * Detect gap type for segment styling
 */
function detectGapType(results: LocalizationResult[]): "solid" | "dashed" {
    if (results.length < 2) return "solid"

    let maxGap = 0
    for (let i = 1; i < results.length; i++) {
        const gap = results[i].start_time_us - results[i - 1].end_time_us
        maxGap = Math.max(maxGap, gap)
    }

    // dashed if there's a medium gap within segment
    if (maxGap > SMALL_GAP_US) {
        return "dashed"
    }

    return "solid"
}

/**
 * Find point at or nearest to time
 */
export function findPointAtTime(
    segment: TrajectorySegment,
    timeUs: number
): { x: number; y: number; z: number } | null {
    if (segment.points.length === 0) return null

    // Check if time is within segment bounds
    if (timeUs < segment.startTimeUs || timeUs > segment.endTimeUs) {
        return null
    }

    // Find two nearest points and interpolate
    for (let i = 0; i < segment.points.length - 1; i++) {
        const p1 = segment.points[i]
        const p2 = segment.points[i + 1]

        if (timeUs >= p1.timeUs && timeUs <= p2.timeUs) {
            const t = (timeUs - p1.timeUs) / (p2.timeUs - p1.timeUs)
            return {
                x: p1.x + (p2.x - p1.x) * t,
                y: p1.y + (p2.y - p1.y) * t,
                z: p1.z + (p2.z - p1.z) * t,
            }
        }
    }

    // Return last point if time is after all points
    const last = segment.points[segment.points.length - 1]
    return { x: last.x, y: last.y, z: last.z }
}

/**
 * Find segment containing time
 */
export function findSegmentAtTime(
    segments: TrajectorySegment[],
    timeUs: number
): { segment: TrajectorySegment; index: number } | null {
    for (let i = 0; i < segments.length; i++) {
        const seg = segments[i]
        if (timeUs >= seg.startTimeUs && timeUs <= seg.endTimeUs) {
            return { segment: seg, index: i }
        }
    }
    return null
}
