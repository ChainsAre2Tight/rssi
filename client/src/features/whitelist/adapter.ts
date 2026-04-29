import type { BackendWhitelist } from "../../types/backend"
import type { Whitelist } from "../../types/general"

export function adaptWhitelist(
    data: BackendWhitelist
): Whitelist {

    const result: Whitelist = {}

    for (const ssid in data.whitelist) {
        const bssids = data.whitelist[ssid]

        result[ssid] = {}

        for (const bssid of bssids) {
            result[ssid][bssid] = true
        }
    }

    return result
}