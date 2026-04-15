import { useEffect, useRef } from "react"
import styles from "./WarningList.module.css"
import { getWarningKey } from "../../utils/warningKey"

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
                    background: `var(--severity-${warning.severity})`
                }}
            />

            <span
                className={styles.label}
                title={warning.signal}
            >
                {warning.signal}
            </span>

            <div className={styles.durationBarContainer}>
                <div
                    className={`${styles.durationBar} ${styles[warning.severity]}`}
                    style={{
                        width: `${Math.max(ratio * 100, 2)}%`
                    }}
                />
            </div>
        </div>
    )
}
