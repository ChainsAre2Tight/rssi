import type { Importance } from "../types/general"

export function getImportanceColor(
    importance: Importance,
    styles: CSSStyleDeclaration
): string {
    switch (importance) {
        case "info":
            return styles.getPropertyValue("--importance-info")
        case "low":
            return styles.getPropertyValue("--importance-low")
        case "medium":
            return styles.getPropertyValue("--importance-medium")
        case "high":
            return styles.getPropertyValue("--importance-high")
        case "critical":
            return styles.getPropertyValue("--importance-critical")
        case "whitelist":
            return styles.getPropertyValue("--importance-whitelist")
        default:
            return styles.getPropertyValue("--importance-info")
    }
}