import type { Severity } from "./general"

export interface BackendReport {
    start_time_us: number
    end_time_us: number
    measurement_id: number
    modalities: Record<string, BackendIncident[]>
}

export interface BackendIncident {
    start_time_us: number
    end_time_us: number
    modality: string
    severity: Severity
    identity: any
    warnings: BackendWarning[]
}

export interface BackendWarning {
    signal: string
    severity: Severity
    metadata: object
    occurrences: {
        start_time_us: number
        end_time_us: number
    }[]
}