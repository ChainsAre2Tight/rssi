const API_BASE = "/api/v1"

function buildQuery(params: Record<string, string | number | undefined>) {
    const search = new URLSearchParams()

    for (const key in params) {
        const value = params[key]
        if (value !== undefined && value !== null) {
            search.append(key, String(value))
        }
    }

    return search.toString()
}

export async function apiGet<T>(
    path: string,
    params?: Record<string, string | number | undefined>
): Promise<T> {

    let url = `${API_BASE}${path}`

    if (params) {
        const query = buildQuery(params)
        if (query) {
            url += `?${query}`
        }
    }

    const res = await fetch(url)

    if (!res.ok) {
        const text = await res.text()
        throw new Error(`API error ${res.status}: ${text}`)
    }

    return res.json()
}