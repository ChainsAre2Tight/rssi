import type { Warning } from "../types/general"

export function getWarningKey(w: Warning): string {
    return `${w.signal}:${JSON.stringify(w.metadata)}`
}
