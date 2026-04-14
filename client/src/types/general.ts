export interface Measurement {
    id: number
    name: string
    description: string
}

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
    signal: string
    type: string
    severity: Severity
    occurrences: Occurrence[]
    metadata: object
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

export type TimeMapper = {
    toX(time: number): number
    toTime(x: number): number

    toGlobalUs(time: number): number
    fromGlobalUs(timeUs: number): number
}

export const SEVERITY_ORDER: Record<Severity, number> = {
    critical: 5,
    high: 4,
    medium: 3,
    low: 2,
    info: 1,
}