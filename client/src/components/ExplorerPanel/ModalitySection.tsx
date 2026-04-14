import { useState } from "react"

import type { Incident, Modality } from "../../types/general"

import IncidentList from "./IncidentList"

type Props = {
    modality: Modality
    incidents: Incident[]
}

export default function ModalitySection({
    modality,
    incidents
}: Props) {

    const [collapsed, setCollapsed] = useState(false)

    const label =
        modality.charAt(0).toUpperCase() +
        modality.slice(1)

    return (

        <div>

            <div
                className="panelHeader"
                onClick={() => setCollapsed(!collapsed)}
                style={{
                    cursor: "pointer",
                    display: "flex",
                    justifyContent: "space-between"
                }}
            >
                <span>
                    {collapsed ? "▶" : "▼"} {label} ({incidents.length})
                </span>
            </div>

            {!collapsed && (
                <IncidentList
                    modality={modality}
                    incidents={incidents}
                />
            )}

        </div>

    )
}
