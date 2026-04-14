import { useState } from "react"

import type { Incident, Modality } from "../../types/general"

import IncidentList from "./IncidentList"
import { formatDurationUs, sumDurationsUs } from "../../utils/duration"
import styles from "./ExplorerPanel.module.css"

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

    const totalDurationUs = sumDurationsUs(incidents)
    const formattedDuration = formatDurationUs(totalDurationUs)

    const maxDurationUs = Math.max(
        ...incidents.map(i => i.endTimeUs - i.startTimeUs),
        1 // safety
    )

    return (

        <div>

            <div
                className={styles.modalityHeader}
                onClick={() => setCollapsed(!collapsed)}
            >
                <span className={styles.modalityHeaderLeft}>
                    {collapsed ? "▶" : "▼"} {label} ({incidents.length})
                </span>

                <span className={styles.modalityHeaderRight}>
                    {formattedDuration}
                </span>
            </div>

            {!collapsed && (
                <IncidentList
                    modality={modality}
                    incidents={incidents}
                    maxDurationUs={maxDurationUs}
                />
            )}

        </div>

    )
}
