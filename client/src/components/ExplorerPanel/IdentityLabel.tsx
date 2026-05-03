import { isWhitelisted } from "../../features/whitelist/utils"
import { useAppStore } from "../../store/useAppStore"

type Props = {
    modality: string
    identity: any
}

export default function IdentityLabel({
    modality,
    identity
}: Props) {

    const measurementId = useAppStore(s => s.context.measurementId)
    const whitelist = useAppStore(s =>
        measurementId !== null
            ? s.whitelist.byMeasurement[measurementId]
            : undefined
    )

    if (modality === "logical") {

        const ssid = identity?.ssid ?? "Unknown SSID"
        const bssid = identity?.bssid ?? ""

        const inWhitelist = isWhitelisted(
            whitelist,
            ssid,
            bssid
        )

        return (
            <span
                title={bssid}
                style={{
                    color: inWhitelist
                        ? "var(--color-text-secondary)"
                        : "var(--color-text)"
                }}
            >
                {ssid} ({bssid})
            </span>
        )
    }

    return <span>Observation</span>
}
