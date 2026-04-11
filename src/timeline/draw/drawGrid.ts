import { getNiceStep } from "../utils/timeGrid"

export function drawGrid(
    ctx: CanvasRenderingContext2D,
    width: number,
    height: number,
    start: number,
    end: number
) {
    const styles = getComputedStyle(document.documentElement)

    const duration = end - start
    const scale = width / duration

    const targetPxPerTick = 100
    const rawStep = targetPxPerTick / scale
    const step = getNiceStep(rawStep)

    const firstTick = Math.floor(start / step) * step

    ctx.strokeStyle = styles.getPropertyValue("--color-border")
    ctx.lineWidth = 1

    for (let t = firstTick; t < end; t += step) {
        const x = Math.round((t - start) * scale) + 0.5

        ctx.beginPath()
        ctx.moveTo(x, 0)
        ctx.lineTo(x, height)
        ctx.stroke()
    }
}
