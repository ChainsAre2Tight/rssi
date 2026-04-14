import type { Measurement } from "../../types/general"

export function loadMockMeasurements(): Measurement[] {
    return [
        {
            id: 1,
            name: "room",
            description: "skibidi?"
        },
        {
            id: 2,
            name: "uni",
            description: "dopdopdop"
        },
        {
            id: 3,
            name: "mooseland",
            description: "yesyesyes"
        }
    ]
}