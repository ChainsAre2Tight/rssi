import { useEffect, useRef } from "react"
import styles from "./WarningList.module.css"
import { getWarningKey } from "../../utils/warningKey"
import { prettifyWarnings } from "../../utils/prettyMapper"

interface Props {
    warning: any
    ratio: number

    selected: boolean

    onSelect: (key: string) => void
    onHover: (key: string | null) => void
}

export function WarningListItem({
    warning,
    ratio,
    selected,
    onSelect,
    onHover,
}: Props) {
    const key = getWarningKey(warning)
    const prettyWarning = prettifyWarnings(warning?.signal)
    const rowRef = useRef<HTMLDivElement | null>(null)

    useEffect(() => {
        if (selected) {
            rowRef.current?.scrollIntoView({
                block: "nearest",
                behavior: "smooth",
            })
        }
    }, [selected])

    return (
        <div
            ref={rowRef}
            className={styles.row}
            data-selected={selected}
            onClick={() => onSelect(key)}
            onMouseEnter={() => onHover(key)}
            onMouseLeave={() => onHover(null)}
        >
            <div
                className={styles.dot}
                style={{
                    background: `var(--importance-${warning.importance})`
                }}
            />

            <span
                className={styles.label}
                title={prettyWarning.name}
            >
                {prettyWarning.name}
            </span>

            <div className={styles.durationBarContainer}>
                <div
                    className={`${styles.durationBar} ${styles[warning.importance]}`}
                    style={{
                        width: `${Math.max(ratio * 100, 2)}%`
                    }}
                />
            </div>
        </div>
    )
}
