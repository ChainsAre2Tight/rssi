import type { Whitelist } from "../../types/general";

export function isWhitelisted(w: Whitelist | undefined, ssid: string, bssid: string) {
    return !!w?.[ssid]?.[bssid]
}
