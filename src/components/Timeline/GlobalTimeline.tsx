import { useAppStore } from "../../store/useAppStore"
import { buildIncidentAdapter } from "../../timeline/adapters/incidents"
import TimelineCanvas from "../../timeline/components/TimelineCanvas"

export default function GlobalTimeline() {
    const incidentsByModality = useAppStore(s => s.report.incidentsByModality)
    const startTimeUs = useAppStore(s => s.report.startTimeUs)
    const endTimeUs = useAppStore(s => s.report.endTimeUs)

    const selectedIncidentId = useAppStore(s => s.selection.incidentId)
    const selectIncident = useAppStore(s => s.selectIncident)

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
                if (!item) {
                    selectIncident(null)
                    return
                }

                if (item.type === "incident") {
                    selectIncident(item.id)
                }
            }}
        />
    )
}
