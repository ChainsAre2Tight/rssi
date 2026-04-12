import { useAppStore } from "../../store/useAppStore"
import { buildWarningAdapter } from "../../timeline/adapters/warnings"
import TimelineCanvas from "../../timeline/components/TimelineCanvas"

export default function WarningTimeline() {

    const incidentId = useAppStore(s => s.selection.incidentId)
    const incidentsByModality = useAppStore(s => s.report.incidentsByModality)

    const incident = Object.values(incidentsByModality)
        .flat()
        .find(i => i.id === incidentId)

    if (!incident) return

    const adapter = buildWarningAdapter({
        incident,
    })

    return (
        <TimelineCanvas
            adapter={adapter}

            externalSelectedKey={null}
            onSelect={() => {}}

            externalHoverKey={null}
            externalHoverTimeUs={null}

            onHoverItem={() => {}}
            onHoverTime={() => {}}
        />
    )
}
