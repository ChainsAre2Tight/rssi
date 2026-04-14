
export const SIGNAL_LABELS: Record<string, string> = {
    unauthorized_ssid: "Unauthorized SSID",
}

export function getSignalLabel(signal: string): string {
    return SIGNAL_LABELS[signal] ?? signal
}