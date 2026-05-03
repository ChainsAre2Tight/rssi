import type { PrettyWarning } from "../types/general"

interface WarningMapping {
    [key: string]: PrettyWarning
}


const mapping: WarningMapping = {
    "typosquat_ssid":           {name: "Typosquat SSID",        description: "SSID uses simslar symbols to look like a whitelisted one"},
    "similar_ssid":             {name: "Similar SSID",          description: "SSID uses a prefix/postfix to look like a whitelisted one"},
    "wrong_ssid":               {name: "Wrong SSID",            description: "Authorized AP broadcasts unauthorized SSID"},
    "unauthorized_ssid":        {name: "Unauthorized SSID",     description: "Broadcastes non-whitelisted SSID"},
    "hidden_ssid":              {name: "Hidden SSID",           description: "AP broadcasts hidden SSID, low activity"},
    "persistent_hidden_ssid":   {name: "Persistent hidden SSID",description: "AP broadcasts hidden SSID, high activity"},
    "beacon_only_ap":           {name: "Beacon-only AP",        description: "AP sent only beacons, no data packets were observed"},
    "high_beacon_ratio":        {name: "High beacon ratio",     description: "AP sent an unusual beacon-to-data packet ratio"},
    "authorized_ap":            {name: "Authorized AP",         description: "This AP is authorized to broadcast this SSID"},

    "euclidean_distance": {
        name: "Euclidean distance",
        description: "Euclidean distance mismatch is likely due to power or distance changes compared to expected values",
    },

    "cosine_distance": {
        name: "Cosine distance",
        description: "Cosine distance repsesent a change in ODFM structure, most likely from multipath structure changes",
    },
}

export function prettifyWarnings(warning: string | null | undefined): PrettyWarning {
    if (!warning) return {name: "None", description: "Missing"}
    return mapping[warning] ?? {name: warning, description: "Missing description"}
}
