import { useState } from "react";

export function useViewport(initial?: { start: number; end: number }) {
    const [viewport, setViewport] = useState(() => ({
        start: initial?.start ?? 0,
        end: initial?.end ?? 1,
    }))

    const duration = viewport.end - viewport.start

    return {
        viewport,
        setViewport,
        duration,
    }
}