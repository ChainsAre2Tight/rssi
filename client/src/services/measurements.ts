import { adaptMeasurement } from "../features/measurements/adapter"
import { apiFetch } from "./apiClient"

interface MeasurementsResponse {
    measurements: {
        measurement_id: number
        name: string
        description: string
        room_id: number
    }[]
}

export async function fetchMeasurements() {
    return apiFetch<MeasurementsResponse>("/measurements", "GET")
}

export type MeasurementPatchRequest = {
    measurement_id: number
    name?: string
    description?: string
}

type ApiMeasurementPatchResponse =
    | {
        status: "ok"
        action: "updated"
        measurement: {
            measurement_id: number
            name: string
            description: string
            room_id: number
        }
    }
    | {
        status: "noop"
        action: "no_changes"
        measurement: {
            measurement_id: number
            name: string
            description: string
            room_id: number
        }
    }
    | {
        status: "noop"
        action: "not_found"
    }

export async function patchMeasurement(
    payload: MeasurementPatchRequest
) {
    const res = await apiFetch<ApiMeasurementPatchResponse>(
        "/measurements",
        "PATCH",
        {
            params: {...payload},
        },
    )

    if ("measurement" in res) {
        return {
            status: res.status,
            action: res.action,
            measurement: adaptMeasurement(res.measurement),
        }
    }

    return res // not_found case
}
