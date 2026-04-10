import { apiGet } from "./apiClient"

export interface ReportRequest {
    measurementId: number
    startTimeUs: number
    endTimeUs: number
    modalities?: string[]
}

export interface ActiveRequest {
    measurementId: number
    offsetS?: number
    modalities?: string[]
}

export async function fetchReport(params: ReportRequest) {

    return apiGet("/reports", {
        measurement_id: params.measurementId,
        start_time_us: params.startTimeUs,
        end_time_us: params.endTimeUs,
        modalities: params.modalities?.join(",")
    })
}

export async function fetchActiveReport(params: ActiveRequest) {

    return apiGet("/active", {
        measurement_id: params.measurementId,
        offset_s: params.offsetS,
        modalities: params.modalities?.join(",")
    })
}
