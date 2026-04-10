
export function toggleTheme() {
    const root = document.documentElement
    const current = root.dataset.theme === "dark" ? "light" : "dark"
    root.dataset.theme = current
}
