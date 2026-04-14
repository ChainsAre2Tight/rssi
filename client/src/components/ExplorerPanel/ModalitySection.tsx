import { useState } from "react"

import type { Incident, Modality } from "../../types/general"

import IncidentList from "./IncidentList"
import { formatDurationUs, sumDurationsUs } from "../../utils/duration"
import styles from "./ExplorerPanel.module.css"

type Props = {
    modality: Modality
    incidents: Incident[]
    totalCount: number
}

export default function ModalitySection({
    modality,
    incidents,
    totalCount,
}: Props) {

    const [collapsed, setCollapsed] = useState(true)

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
                <span>
                    {collapsed ? "▶" : "▼"} {label} ({incidents.length} / {totalCount})
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
