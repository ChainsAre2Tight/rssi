type Props = {
    modality: string
    identity: any
}

export default function IdentityLabel({
    modality,
    identity
}: Props) {

    if (modality === "logical") {

        const ssid = identity?.ssid ?? "Unknown SSID"
        const bssid = identity?.bssid ?? ""

        return (
            <span title={bssid}>
                {ssid} ({bssid})
            </span>
        )
    }

    return <span>Incident</span>
}
