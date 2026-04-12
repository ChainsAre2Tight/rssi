import { useEffect, useRef } from "react"
import type { TimelineAdapterResult, TimelineEventType } from "../types"

interface Params {
    adapter: TimelineAdapterResult

    externalHoverKey: string | null
    externalHoverTimeUs: number | null

    onHoverItem: (item: {
        key: string
        type: TimelineEventType
        id: string
    } | null) => void

    onHoverTime: (timeUs: number | null) => void

    setHoveredKey: (key: string | null) => void
    setExternalCursorTimeUs: (timeUs: number | null) => void
}

export function useTimelineHoverSync({
    adapter,
    externalHoverKey,
    externalHoverTimeUs,
    onHoverItem,
    onHoverTime,
    setHoveredKey,
    setExternalCursorTimeUs,
}: Params) {
    const isInternalUpdate = useRef(false)

    const lastKeyRef = useRef<string | null>(null)
    const lastTimeRef = useRef<number | null>(null)

    useEffect(() => {
        if (isInternalUpdate.current) {
            isInternalUpdate.current = false
            return
        }

        setHoveredKey(externalHoverKey)
    }, [externalHoverKey])

    useEffect(() => {

        // TODO: investigate mapping discrepanies
        setExternalCursorTimeUs(externalHoverTimeUs)
    }, [externalHoverTimeUs])

    function handleInternalHover(
        key: string | null,
        timeUs: number | null
    ) {
        isInternalUpdate.current = true

        // ---- ITEM ----
        if (key !== lastKeyRef.current) {
            lastKeyRef.current = key

            if (!key) {
                onHoverItem(null)
            } else {
                const item = adapter.index.byKey.get(key)

                if (item) {
                    onHoverItem({
                        key: item.key,
                        type: item.type,
                        id: item.id,
                    })
                } else {
                    onHoverItem(null)
                }
            }
        }

        // ---- TIME (quantized) ----
        if (timeUs !== null) {
            const rounded = Math.round(timeUs / 100_000) * 100_000

            if (rounded !== lastTimeRef.current) {
                lastTimeRef.current = rounded
                onHoverTime(rounded)
            }
        } else {
            if (lastTimeRef.current !== null) {
                lastTimeRef.current = null
                onHoverTime(null)
            }
        }
    }

    return {
        handleInternalHover,
    }
}
