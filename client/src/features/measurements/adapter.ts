import type { Measurement } from "../../types/general"

interface ApiMeasurement {
    measurement_id: number
    name: string
    description: string
    room_id: number
}

export function adaptMeasurements(
    items: ApiMeasurement[]
): Measurement[] {
    return items.map(m => ({
        id: m.measurement_id,
        name: m.name,
        description: m.description,
    }))
}
