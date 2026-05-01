import { fetchWhitelist } from "../../services/apiWhitelist"
import type { Whitelist } from "../../types/general"
import { adaptWhitelist } from "./adapter"


export async function loadWhitelist(
    measurementId: number
): Promise<Whitelist> {

    const raw = await fetchWhitelist(measurementId)
    const adapted = adaptWhitelist(raw)
    return adapted
}
