import { fetchActiveReport, fetchReport } from "../../services/reportApi"
import type { BackendReport } from "../../types/backend"
import { adaptReport } from "./adapter"

interface LoadReportParams {
    measurementId: number
    startTimeUs?: number
    endTimeUs?: number
    offsetS?: number
}

export async function loadReport({
    measurementId,
    startTimeUs,
    endTimeUs,
    offsetS,
}: LoadReportParams) {

    let raw: BackendReport

    if (offsetS !== undefined) {
        // active-style
        raw = await fetchActiveReport({
            measurementId,
            offsetS,
        }) as BackendReport
    } else {
        // report-style
        raw = await fetchReport({
            measurementId,
            startTimeUs: startTimeUs!,
            endTimeUs: endTimeUs!,
        }) as BackendReport
    }

    return adaptReport(raw)
}
