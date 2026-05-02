import type { BackendWhitelist } from "../types/backend"
import { apiFetch } from "./apiClient"

export async function fetchWhitelist(
    measurementId: number
): Promise<BackendWhitelist> {
    return apiFetch("/whitelist", "GET", {params: {
        measurement_id: measurementId
    }})
}

export type WhitelistAction =
    | "ssid_created"
    | "bssid_added"
    | "already_exists"
    | "ssid_removed"
    | "bssid_removed"
    | "not_found"
    | "renamed"
    | "merged"
    | "same_name"

export interface WhitelistActionResponse {
    action: WhitelistAction
    status: "ok" | "noop"
}


// TODO: fix for hidden ssids
export async function addWhitelistPair(
    measurementId: number,
    ssid: string,
    bssid: string
) {
    return await apiFetch<WhitelistActionResponse>("/whitelist", "POST", {params: {
        measurement_id: measurementId,
        ssid,
        bssid
    }})
}

// TODO: fix for hidden ssids
export async function removeWhitelistPair(
    measurementId: number,
    ssid: string,
    bssid: string
) {
    return apiFetch<WhitelistActionResponse>("/whitelist", "DELETE", {params: {
        measurement_id: measurementId,
        ssid,
        bssid
    }})
}

export async function addWhitelistSSID(
    measurementId: number,
    ssid: string
) {
    return apiFetch<WhitelistActionResponse>("/whitelist", "POST", {params: {
        measurement_id: measurementId,
        ssid
    }})
}

export async function removeWhitelistSSID(
    measurementId: number,
    ssid: string
) {
    return apiFetch<WhitelistActionResponse>("/whitelist", "DELETE", {params: {
        measurement_id: measurementId,
        ssid
    }})
}

export async function removeWhitelistBSSID(
    measurementId: number,
    ssid: string,
    bssid: string,
    removeEmptySSID: boolean = true
) {
    return apiFetch<WhitelistActionResponse>("/whitelist", "DELETE", {params: {
        measurement_id: measurementId,
        ssid,
        bssid,
        remove_empty_ssid: removeEmptySSID
    }})
}

export async function renameWhitelistSSID(
    measurementId: number,
    ssid: string,
    newSSID: string
) {
    return apiFetch<WhitelistActionResponse>("/whitelist", "PATCH", {params: {
        measurement_id: measurementId,
        ssid,
        new_ssid: newSSID
    }})
}
