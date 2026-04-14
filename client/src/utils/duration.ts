export function getIncidentDurationUs(i: { startTimeUs: number; endTimeUs: number }) {
    return i.endTimeUs - i.startTimeUs
}

export function sumDurationsUs(items: { startTimeUs: number; endTimeUs: number }[]) {
    return items.reduce((acc, i) => acc + getIncidentDurationUs(i), 0)
}

export function formatDurationUs(us: number) {
    const totalSec = Math.floor(us / 1_000_000)

    const h = Math.floor(totalSec / 3600)
    const m = Math.floor((totalSec % 3600) / 60)
    const s = totalSec % 60

    if (h > 0) return `${h}h ${m}m`
    if (m > 0) return `${m}m ${s}s`
    return `${s}s`
}
