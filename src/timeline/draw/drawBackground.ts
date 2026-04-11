export function drawBackground(
    ctx: CanvasRenderingContext2D,
    width: number,
    height: number
) {
    const styles = getComputedStyle(document.documentElement)

    ctx.fillStyle = styles.getPropertyValue("--color-bg")
    ctx.fillRect(0, 0, width, height)
}
