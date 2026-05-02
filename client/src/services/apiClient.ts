const API_BASE = "/api/v1"

function buildQuery(params: Record<string, string | number | undefined | boolean>) {
    const search = new URLSearchParams()

    for (const key in params) {
        const value = params[key]
        if (value !== undefined && value !== null) {
            search.append(key, String(value))
        }
    }

    return search.toString()
}


export async function apiFetch<T>(
    path: string,
    method: "GET" | "POST" | "DELETE" | "PATCH",
    options?: {
        params?: Record<string, string | number | boolean | undefined>
        body?: unknown
    }
): Promise<T> {

    let url = `${API_BASE}${path}`

    if (options?.params) {
        const query = buildQuery(options.params)
        if (query) {
            url += `?${query}`
        }
    }

    const res = await fetch(url, {
        method,
        headers: options?.body
            ? { "Content-Type": "application/json" }
            : undefined,
        body: options?.body
            ? JSON.stringify(options.body)
            : undefined
    })

    if (!res.ok) {
        const text = await res.text()
        throw new Error(`API error ${res.status}: ${text}`)
    }

    return res.json()
}
