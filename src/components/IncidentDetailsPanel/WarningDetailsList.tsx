import { useAppStore } from "../../store/useAppStore"
import WarningRow from "./WarningRow"

const sevOrder = {
    critical: 5,
    high: 4,
    medium: 3,
    low: 2,
    info: 1
}

export default function WarningDetailsList() {

    const incidentId = useAppStore(s => s.selection.incidentId)
    const incidentsByModality = useAppStore(s => s.report.incidentsByModality)

    const incident = Object.values(incidentsByModality)
        .flat()
        .find(i => i.id === incidentId)

    if (!incident) {
        return <div className="panelBody">No warnings</div>
    }

    const warnings = [...incident.warnings].sort(
        (a, b) => sevOrder[b.severity] - sevOrder[a.severity]
    )

    return (
        <div className="panel">

            <div className="panelHeader">
                Warnings
            </div>

            <div className="panelBody">

                {warnings.map(w => (
                    <WarningRow
                        key={`${w.signal}:${JSON.stringify(w.metadata)}`}
                        warning={w}
                        incidentId={incident.id}
                    />
                ))}

            </div>

        </div>
    )
}
