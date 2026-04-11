import { useState } from "react"

export function useViewport() {
    const [viewport, setViewport] = useState({
        start: 0,
        end: 300, // 5 minutes
    })

    const duration = viewport.end - viewport.start

    return {
        viewport,
        setViewport,
        duration,
    }
}