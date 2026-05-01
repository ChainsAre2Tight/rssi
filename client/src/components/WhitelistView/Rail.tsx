import styles from "./Rail.module.css"

export function IRail() {
    return <div className={styles.i} />
}

export function TRail() {
    return (
        <div className={styles.t}>
            <div className={styles.vertical} />
            <div className={styles.horizontal} />
        </div>
    )
}

export function LRail() {
    return (
        <div className={styles.l}>
            <div className={styles.vertical} />
            <div className={styles.horizontal} />
        </div>
    )
}
