import type { Warning } from "../types/general"

export function getWarningKey(w: Warning): string {
    return `${w.id}:${w.signal}:${w.importance}:${JSON.stringify(w.metadata)}`
}
