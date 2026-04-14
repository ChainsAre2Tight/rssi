import { useRef } from "react"

type Props = {
    onDrag: (delta: number) => void
}

export default function VerticalResizer({ onDrag }: Props) {

    const startX = useRef<number | null>(null)

    function onMouseDown(e: React.MouseEvent) {

        startX.current = e.clientX

        function onMove(ev: MouseEvent) {

            if (startX.current === null) return

            const delta = ev.clientX - startX.current

            startX.current = ev.clientX

            onDrag(delta)
        }

        function onUp() {

            window.removeEventListener("mousemove", onMove)
            window.removeEventListener("mouseup", onUp)

            startX.current = null
        }

        window.addEventListener("mousemove", onMove)
        window.addEventListener("mouseup", onUp)
    }

    return (
        <div
            style={{
                width: "4px",
                cursor: "col-resize",
                background: "var(--color-border)"
            }}
            onMouseDown={onMouseDown}
        />
    )
}
