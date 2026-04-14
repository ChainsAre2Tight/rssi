import { apiGet } from "./apiClient"

interface MeasurementsResponse {
    measurements: {
        measurement_id: number
        name: string
        description: string
        room_id: number
    }[]
}

export async function fetchMeasurements() {
    return apiGet<MeasurementsResponse>("/measurements")
}
