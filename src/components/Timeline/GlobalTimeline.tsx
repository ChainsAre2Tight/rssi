import { useAppStore } from "../../store/useAppStore"
import { buildIncidentAdapter } from "../../timeline/adapters/incidents"
import TimelineCanvas from "../../timeline/components/TimelineCanvas"

export default function GlobalTimeline() {
    const incidentsByModality = useAppStore(s => s.report.incidentsByModality)
    const startTimeUs = useAppStore(s => s.report.startTimeUs)
    const endTimeUs = useAppStore(s => s.report.endTimeUs)

    const adapter = buildIncidentAdapter({
        incidentsByModality: incidentsByModality,
        reportStartUs: startTimeUs!,
        reportEndUs: endTimeUs!,
    })

    return (
        <div style={{ width: "100%", height: "100%" }}>
            <TimelineCanvas adapter={adapter} />
        </div>
    )
}