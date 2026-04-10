import styles from "./TopBar.module.css"

import MeasurementSelector from "./MeasurementSelector"
import ModeToggle from "./ModeToggle"

export default function TopBar() {
    return (
        <div className={styles.root}>
            <div className={styles.left}>
                <MeasurementSelector />
                <ModeToggle />
            </div>

            <div className={styles.right}>
                {/* mode specific controls will go here */}
            </div>
        </div>
    )
}