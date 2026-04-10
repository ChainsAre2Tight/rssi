import { toggleTheme } from "../../utils/theme"

import styles from "./ThemeToggle.module.css"

export default function ThemeToggle() {

    function handleClick() {
        toggleTheme()
    }

    return (
        <button
            className={styles.button}
            onClick={handleClick}
        >
            <span className={styles.label}></span>
        </button>
    )
}