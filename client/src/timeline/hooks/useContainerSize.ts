import { useEffect, useState } from "react"

export function useContainerSize(
    ref: React.RefObject<HTMLElement>
) {
    const [size, setSize] = useState({
        width: 0,
        height: 0,
    })

    useEffect(() => {
        const el = ref.current
        if (!el) return

        const observer = new ResizeObserver((entries) => {
            const entry = entries[0]
            const { width, height } = entry.contentRect

            setSize({
                width,
                height,
            })
        })

        observer.observe(el)

        return () => observer.disconnect()
    }, [ref])

    return size
}
