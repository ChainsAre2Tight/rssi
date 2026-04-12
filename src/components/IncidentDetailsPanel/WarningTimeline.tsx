import { useAppStore } from "../../store/useAppStore"
import { buildWarningAdapter } from "../../timeline/adapters/warnings"
import TimelineCanvas from "../../timeline/components/TimelineCanvas"

export default function WarningTimeline() {
    const incidentId = useAppStore(s => s.selection.incidentId)
    const incidentsByModality = useAppStore(s => s.report.incidentsByModality)

    const warningKey = useAppStore(s => s.selection.warningKey)
    const hoveredWarningKey = useAppStore(s => s.hover.warningKey)
    const hoverTimeUs = useAppStore(s => s.hover.timelineTimeUs)

    const selectWarning = useAppStore(s => s.selectWarning)
    const hoverWarning = useAppStore(s => s.hoverWarning)
    const setTimelineCursor = useAppStore(s => s.setTimelineCursor)

    const incident = Object.values(incidentsByModality)
        .flat()
        .find(i => i.id === incidentId)

    if (!incident) return null

    const adapter = buildWarningAdapter({
        incident,
    })

    return (
        <TimelineCanvas
            adapter={adapter}

            externalSelectedKey={warningKey}
            onSelect={(item) => {
                if (!item) {
                    selectWarning(null)
                    return
                }

                if (item.type === "warning") {
                    selectWarning(item.key)
                }
            }}

            externalHoverKey={hoveredWarningKey}
            externalHoverTimeUs={hoverTimeUs}

            onHoverItem={(item) => {
                hoverWarning(item?.key ?? null)
            }}

            onHoverTime={(timeUs) => {
                setTimelineCursor(timeUs)
            }}
        />
    )
}