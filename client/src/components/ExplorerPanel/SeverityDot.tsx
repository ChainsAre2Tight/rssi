type Props = {
    severity: string
}

export default function SeverityDot({ severity }: Props) {

    return (
        <div
            style={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                background: `var(--severity-${severity})`
            }}
        />
    )
}
