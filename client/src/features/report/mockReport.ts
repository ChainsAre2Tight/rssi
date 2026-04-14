import reportJson from "../../mocks/report.json"
import { adaptReport } from "./adapter"

export function loadMockReport() {
    return adaptReport(reportJson as any)
}