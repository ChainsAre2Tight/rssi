import { apiGet } from "./apiClient"

export interface LocalizationResult {
    window_id: number
    bssid: string
    start_time_us: number
    end_time_us: number
    estimated_position: [number, number, number]
    estimated_p0: number
    device_count: number
    converged: boolean
    metadata?: Record<string, any>
}

export interface LocalizationData {
    measurement_id: number
    modality: string
    bssid: string
    completed: number
    pending: number
    processing: number
    failed: number
    locations: LocalizationResult[]
}

export interface Sensor {
    name: string
    mac: string
    description: string
    x: number
    y: number
    z: number
}

export interface SensorsResponse {
    measurement_id: number
    sensors: Sensor[]
}

export async function fetchLocalization(params: {
    measurementId: number
    startTimeUs: number
    endTimeUs: number
    bssid: string
    modality?: string
}): Promise<LocalizationData> {
    return apiGet("/localizations", {
        measurement_id: params.measurementId,
        start_time_us: params.startTimeUs,
        end_time_us: params.endTimeUs,
        bssid: params.bssid,
        modality: params.modality,
    })
}

export async function requestLocalization(params: {
    measurementId: number
    startTimeUs: number
    endTimeUs: number
    bssid: string
    modality?: string
}): Promise<{ measurement_id: number; jobs_created: number; jobs_ignored: number; pending: number }> {
    const url = "/localize"
    const queryParams = new URLSearchParams({
        measurement_id: String(params.measurementId),
        start_time_us: String(params.startTimeUs),
        end_time_us: String(params.endTimeUs),
        bssid: params.bssid,
        modality: params.modality || "logical",
    })

    const res = await fetch(`/api/v1${url}?${queryParams.toString()}`, {
        method: "POST",
    })

    if (!res.ok) {
        const text = await res.text()
        throw new Error(`API error ${res.status}: ${text}`)
    }

    return res.json()
}

export async function fetchSensors(measurementId: number): Promise<Sensor[]> {
    const response: SensorsResponse = await apiGet("/sensors", {
        measurement_id: measurementId,
    })
    return response.sensors
}
