import { useRef, useState } from "react"
import styles from "./Resizer.module.css"

type Props = {
    onDrag: (delta: number) => void
}

export default function HorizontalResizer({ onDrag }: Props) {

    const startY = useRef<number | null>(null)
    const [dragging, setDragging] = useState(false)

    function onMouseDown(e: React.MouseEvent) {

        startY.current = e.clientY
        setDragging(true)

        document.body.style.userSelect = "none"

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
            setDragging(false)

            document.body.style.userSelect = ""
        }

        window.addEventListener("mousemove", onMove)
        window.addEventListener("mouseup", onUp)
    }

    return (
        <div
            className={`${styles.root} ${styles.horizontal}`}
            data-dragging={dragging}
            onMouseDown={onMouseDown}
            style={{
                height: "8px",
                cursor: "row-resize"
            }}
        >
            <div
                className={styles.line}
                style={{
                    height: "2px",
                    width: "100%"
                }}
            />
        </div>
    )
}
