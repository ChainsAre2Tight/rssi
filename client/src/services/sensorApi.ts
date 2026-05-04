import { apiFetch } from "./apiClient"

export interface SensorPatchResponse {
    status: "ok" | "noop"
    updated_description?: true
    updated_positions?: true
}

export async function patchSensorDescription({
    measurementId,
    device,
    description,
} : {
    measurementId: number
    device: string
    description: string,
}): Promise<SensorPatchResponse> {
    const response: SensorPatchResponse = await apiFetch("/sensors", "PATCH", {params: {
        measurement_id: measurementId,
        device,
        description
    }})
    return response
}

export async function patchSensorPosition({
    measurementId,
    device,
    x, y, z
} : {
    measurementId: number
    device: string
    x: number,
    y: number,
    z: number
}): Promise<SensorPatchResponse> {
    const response: SensorPatchResponse = await apiFetch("/sensors", "PATCH", {params: {
        measurement_id: measurementId,
        device,
        x, y, z,
    }})
    return response
}
