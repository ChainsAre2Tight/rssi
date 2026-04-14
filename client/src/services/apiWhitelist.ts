import { apiGet } from "./apiClient"

export async function fetchWhitelist(measurementId: number) {

    return apiGet("/whitelist", {
        measurement_id: measurementId
    })
}