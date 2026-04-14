import { useRef, useState } from "react"
import styles from "./Resizer.module.css"

type Props = {
    onDrag: (delta: number) => void
}

export default function VerticalResizer({ onDrag }: Props) {

    const startX = useRef<number | null>(null)
    const [dragging, setDragging] = useState(false)

    function onMouseDown(e: React.MouseEvent) {

        startX.current = e.clientX
        setDragging(true)

        // disable text selection
        document.body.style.userSelect = "none"

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
            setDragging(false)

            // restore selection
            document.body.style.userSelect = ""
        }

        window.addEventListener("mousemove", onMove)
        window.addEventListener("mouseup", onUp)
    }

    return (
        <div
            className={`${styles.root} ${styles.vertical}`}
            data-dragging={dragging}
            onMouseDown={onMouseDown}
            style={{
                width: "8px",
                cursor: "col-resize"
            }}
        >
            <div
                className={styles.line}
                style={{
                    width: "2px",
                    height: "100%"
                }}
            />
        </div>
    )
}
