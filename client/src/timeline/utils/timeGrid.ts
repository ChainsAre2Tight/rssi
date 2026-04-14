export function getNiceStep(rawStep: number): number {
    const steps = [1, 2, 5, 10, 30, 60, 120, 300, 600]

    for (const step of steps) {
        if (rawStep <= step) return step
    }

    return steps[steps.length - 1]
}