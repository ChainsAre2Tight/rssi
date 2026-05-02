import { apiFetch } from "./apiClient";

export type DetectionApiResponse = {
    status: string
}

export async function deleteDetection(
    measurementId: number,
) {
    return await apiFetch<DetectionApiResponse>("/detection", "DELETE", {params: {
        measurement_id: measurementId,
    }})
}
