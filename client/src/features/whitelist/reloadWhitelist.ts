import { useAppStore } from "../../store/useAppStore"
import { loadWhitelist } from "./loadWhitelist"

export async function reloadWhitelist(measurementId: number) {
    const setWhitelist = useAppStore.getState().setWhitelist
    const setLoading = useAppStore.getState().setWhitelistLoading

    setLoading(true)

    try {
        const data = await loadWhitelist(measurementId)
        setWhitelist(measurementId, data)
    } catch (e) {
        console.error("Failed to reload whitelist", e)
    } finally {
        setLoading(false)
    }
}
