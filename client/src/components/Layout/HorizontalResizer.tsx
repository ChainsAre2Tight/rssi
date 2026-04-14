import { useRef } from "react"

type Props = {
    onDrag: (delta: number) => void
}

export default function HorizontalResizer({ onDrag }: Props) {

    const startY = useRef<number | null>(null)

    function onMouseDown(e: React.MouseEvent) {

        startY.current = e.clientY

        function onMove(ev: MouseEvent) {

            if (startY.current === null) return

            const delta = ev.clientY - startY.current

            startY.current = ev.clientY

            onDrag(delta)
        }

        function onUp() {

            window.removeEventListener("mousemove", onMove)
            window.removeEventListener("mouseup", onUp)

            startY.current = null
        }

        window.addEventListener("mousemove", onMove)
        window.addEventListener("mouseup", onUp)
    }

    return (
        <div
            style={{
                height: "4px",
                cursor: "row-resize",
                background: "var(--color-border)"
            }}
            onMouseDown={onMouseDown}
        />
    )
}
