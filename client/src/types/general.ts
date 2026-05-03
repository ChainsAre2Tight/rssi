export interface Measurement {
    id: number
    name: string
    description: string
}

export type Modality = "logical" | "physical"

export type Importance =
    | "info"
    | "low"
    | "medium"
    | "high"
    | "critical"
    | "whitelist"

export const SEVERITIES: Importance[] = [
  "whitelist",
  "info",
  "low",
  "medium",
  "high",
  "critical",
];

export interface Occurrence {
    startTimeUs: number
    endTimeUs: number
}

export interface Warning {
    id: string
    signal: string
    type: string
    importance: Importance
    occurrences: Occurrence[]
    metadata: object
}

export interface Incident {
    id: string
    modality: Modality
    startTimeUs: number
    endTimeUs: number
    importance: Importance
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

export const IMPORTANCE_ORDER: Record<Importance, number> = {
    critical: 5,
    high: 4,
    medium: 3,
    low: 2,
    info: 1,
    whitelist: -1,
}

export interface PrettyWarning {
    name: string
    description: string
}

export type Whitelist = Record<string, Record<string, boolean>>
