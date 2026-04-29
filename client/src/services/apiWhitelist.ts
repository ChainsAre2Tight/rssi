import type { BackendWhitelist } from "../types/backend"
import { apiFetch } from "./apiClient"

export async function fetchWhitelist(
    measurementId: number
): Promise<BackendWhitelist> {
    return apiFetch("/whitelist", "GET", {
        measurement_id: measurementId
    })
}

export interface WhitelistActionResponse {
    action: string
    status: string
}

export async function addWhitelistPair(
    measurementId: number,
    ssid: string,
    bssid: string
) {
    return await apiFetch<WhitelistActionResponse>("/whitelist", "POST", {
        measurement_id: measurementId,
        ssid,
        bssid
    })


}

export async function removeWhitelistPair(
    measurementId: number,
    ssid: string,
    bssid: string
) {
    return apiFetch<WhitelistActionResponse>("/whitelist", "DELETE", {
        measurement_id: measurementId,
        ssid,
        bssid
    })
}