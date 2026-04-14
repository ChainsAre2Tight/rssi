import { useEffect, useRef } from "react"
import type { TimelineAdapterResult } from "../types"

interface Params {
    adapter: TimelineAdapterResult

    externalSelectedKey: string | null

    onSelect: (item: { key: string; type: "incident" | "warning"; id: string } | null) => void

    setSelectedKey: (key: string | null) => void
}

export function useTimelineSync({
    adapter,
    externalSelectedKey,
    onSelect,
    setSelectedKey,
}: Params) {
    const isInternalUpdate = useRef(false)

    // 🔹 External → Internal
    useEffect(() => {
        if (isInternalUpdate.current) {
            isInternalUpdate.current = false
            return
        }

        setSelectedKey(externalSelectedKey)
    }, [externalSelectedKey])

    // 🔹 Internal → External
    function handleInternalSelect(key: string | null) {
        isInternalUpdate.current = true

        setSelectedKey(key)
        
        if (!key) {
            onSelect(null)
            return
        }

        const item = adapter.index.byKey.get(key)

        if (!item) {
            onSelect(null)
            return
        }

        onSelect({
            key: item.key,
            type: item.type,
            id: item.id,
        })
    }

    return {
        handleInternalSelect,
    }
}
