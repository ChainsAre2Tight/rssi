type Props = {
    importance: string
}

export default function ImportanceDot({ importance }: Props) {

    return (
        <div
            style={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                background: `var(--importance-${importance})`
            }}
        />
    )
}
