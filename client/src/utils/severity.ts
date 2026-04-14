import type { Severity } from "../types/general"

export function getSeverityColor(
    severity: Severity,
    styles: CSSStyleDeclaration
): string {
    switch (severity) {
        case "info":
            return styles.getPropertyValue("--severity-info")
        case "low":
            return styles.getPropertyValue("--severity-low")
        case "medium":
            return styles.getPropertyValue("--severity-medium")
        case "high":
            return styles.getPropertyValue("--severity-high")
        case "critical":
            return styles.getPropertyValue("--severity-critical")
        default:
            return styles.getPropertyValue("--severity-info")
    }
}