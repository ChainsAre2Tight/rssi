export function initTheme() {

    const root = document.documentElement

    const saved = localStorage.getItem("theme")

    if (saved === "dark" || saved === "light") {
        root.dataset.theme = saved
        return
    }

    const prefersDark =
        window.matchMedia("(prefers-color-scheme: dark)").matches

    root.dataset.theme = prefersDark ? "dark" : "light"

    const media = window.matchMedia("(prefers-color-scheme: dark)")

    media.addEventListener("change", (e) => {

        const saved = localStorage.getItem("theme")

        if (saved) return

        document.documentElement.dataset.theme =
            e.matches ? "dark" : "light"

    })
}

export function toggleTheme() {

    const root = document.documentElement

    const next =
        root.dataset.theme === "dark"
            ? "light"
            : "dark"

    root.dataset.theme = next

    localStorage.setItem("theme", next)
}
