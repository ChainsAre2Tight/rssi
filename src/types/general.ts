export type Modality = "logical" | "physical"

export type Severity =
    | "info"
    | "low"
    | "medium"
    | "high"
    | "critical"

export interface Occurrence {
    startTimeUs: number
    endTimeUs: number
}

export interface Warning {
    type: string
    severity: Severity
    occurrences: Occurrence[]
    metadata: Record<string, any>
}

export interface Incident {
    id: string
    modality: Modality
    startTimeUs: number
    endTimeUs: number
    severity: Severity
    identity: IncidentIdentity | null
    warnings: Warning[]
}

export interface IncidentIdentity {
    [key: string]: any
}