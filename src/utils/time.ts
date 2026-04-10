function pad(n: number): string {
    return n.toString().padStart(2, "0")
}

export function formatDateTime(us: number): string {

    const d = new Date(us / 1000)

    return (
        `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ` +
        `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
    )
}

export function formatTime(us: number): string {

    const d = new Date(us / 1000)

    return `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

export function formatOccurrenceRange(
    startUs: number,
    endUs: number
): string {

    const start = new Date(startUs / 1000)
    const end = new Date(endUs / 1000)

    const sameDate =
        start.getFullYear() === end.getFullYear() &&
        start.getMonth() === end.getMonth() &&
        start.getDate() === end.getDate()

    if (sameDate) {
        return `${formatTime(startUs)} — ${formatTime(endUs)}`
    }

    return `${formatDateTime(startUs)} — ${formatDateTime(endUs)}`
}
