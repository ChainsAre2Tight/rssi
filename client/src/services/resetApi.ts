import { apiFetch } from "./apiClient";

export type ResetApiResponse = {
    status: string
}

export async function resetDetection(
    measurementId: number,
) {
    return await apiFetch<ResetApiResponse>("/detection", "DELETE", {params: {
        measurement_id: measurementId,
    }})
}

export async function resetCSI(
    measurementId: number,
) {
    return await apiFetch<ResetApiResponse>("/csi", "DELETE", {params: {
        measurement_id: measurementId,
    }})
}

export async function resetLocalization(
    measurementId: number,
) {
    return await apiFetch<ResetApiResponse>("/localizations", "DELETE", {params: {
        measurement_id: measurementId,
    }})
}

