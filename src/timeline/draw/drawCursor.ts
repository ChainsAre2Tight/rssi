export function drawCursor(
    ctx: CanvasRenderingContext2D,
    height: number,
    cursorX: number | null,
    zoomAnchorX: number | null,
    isZooming: boolean
) {
    const styles = getComputedStyle(document.documentElement)

    if (isZooming && zoomAnchorX !== null) {
        const x = Math.round(zoomAnchorX) + 0.5

        ctx.strokeStyle = styles.getPropertyValue("--color-accent")
        ctx.lineWidth = 2

        ctx.beginPath()
        ctx.moveTo(x, 0)
        ctx.lineTo(x, height)
        ctx.stroke()

        return
    }

    if (cursorX !== null) {
        const x = Math.round(cursorX) + 0.5

        ctx.strokeStyle = styles.getPropertyValue("--color-accent")
        ctx.lineWidth = 1

        ctx.beginPath()
        ctx.moveTo(x, 0)
        ctx.lineTo(x, height)
        ctx.stroke()
    }
}
