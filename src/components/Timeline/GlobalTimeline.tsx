import { useAppStore } from "../../store/useAppStore"
import { buildIncidentAdapter } from "../../timeline/adapters/incidents"
import TimelineCanvas from "../../timeline/components/TimelineCanvas"

export default function GlobalTimeline() {
    const incidentsByModality = useAppStore(s => s.report.incidentsByModality)
    const startTimeUs = useAppStore(s => s.report.startTimeUs)
    const endTimeUs = useAppStore(s => s.report.endTimeUs)

    const selectedIncidentId = useAppStore(s => s.selection.incidentId)
    const selectIncident = useAppStore(s => s.selectIncident)

    const hoverIncident = useAppStore(s => s.hoverIncident)
    const setTimelineCursor = useAppStore(s => s.setTimelineCursor)

    const hoveredIncidentId = useAppStore(s => s.hover.incidentId)
    const hoverTimeUs = useAppStore(s => s.hover.timelineTimeUs)

    const adapter = buildIncidentAdapter({
        incidentsByModality,
        reportStartUs: startTimeUs!,
        reportEndUs: endTimeUs!,
        minGapS: 10,
    })

    return (
        <TimelineCanvas
            adapter={adapter}

            externalSelectedKey={selectedIncidentId}
            onSelect={(item) => {
                if (!item) return selectIncident(null)
                if (item.type === "incident") selectIncident(item.id)
            }}

            externalHoverKey={hoveredIncidentId}
            externalHoverTimeUs={hoverTimeUs}

            onHoverItem={(item) => {
                hoverIncident(item?.id ?? null)
            }}

            onHoverTime={(timeUs) => {
                setTimelineCursor(timeUs)
            }}
        />
    )
}
