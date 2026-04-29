import type { Whitelist } from "../../types/general";

export function isWhitelisted(w: Whitelist | undefined, ssid: string, bssid: string) {
    const result = !!w?.[ssid]?.[bssid]
    console.log(ssid, bssid, result)
    return result
}
