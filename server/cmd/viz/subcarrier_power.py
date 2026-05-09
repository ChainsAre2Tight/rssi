#!/usr/bin/env python3
"""
CSI Fingerprint Viewer

Plots per‑sensor amplitude profiles (reference vs selected window) as vertical bar pairs.

Usage:
    python view_csi_fingerprint.py --measurement_id 1 --bssid "AA:BB:CC:DD:EE:FF" --window_id 42
"""

import argparse
import sys

import matplotlib.pyplot as plt
import numpy as np

from storage.csi_fingerprints import get_reference_fingerprint, loads
import storage


def parse_args():
    parser = argparse.ArgumentParser(description="Plot CSI fingerprint amplitude profiles")
    parser.add_argument("--measurement_id", type=int, required=True, help="Measurement ID")
    parser.add_argument("--bssid", type=str, required=True, help="BSSID of the AP")
    parser.add_argument("--window_id", type=int, required=True, help="Window ID to compare with reference")
    return parser.parse_args()


def get_fingerprint_by_window_id(conn, window_id: int, bssid: str):
    """Retrieve fingerprint for a given window_id and bssid."""
    # This mimics your get_fingerprint but we also verify measurement_id matches
    row = conn.execute(
        """
        SELECT id, measurement_id, window_id, bssid, is_reference,
               vector, sensor_names_json, metadata_json
        FROM csi_fingerprints
        WHERE window_id = ? AND bssid = ?
        LIMIT 1
        """,
        (window_id, bssid),
    ).fetchone()
    if not row:
        return None
    # Reconstruct the fingerprint object (simplified)
    return {
        "id": row[0],
        "measurement_id": row[1],
        "window_id": row[2],
        "bssid": row[3],
        "is_reference": bool(row[4]),
        "vector": row[5],
        "sensor_names": loads(row[6]),
        "metadata": loads(row[7]) if row[7] else {},
    }


def main():
    args = parse_args()
    with storage.Session() as conn:

        # Load reference fingerprint
        ref_fp = get_reference_fingerprint(conn, args.measurement_id, args.bssid)
        if ref_fp is None:
            print(f"Error: No reference fingerprint found for measurement {args.measurement_id}, BSSID {args.bssid}")
            sys.exit(1)

        # Load selected window fingerprint
        # Use get_fingerprint_by_window_id because get_fingerprint only requires window_id and bssid,
        # but we also ensure it belongs to the same measurement.
        test_fp = get_fingerprint_by_window_id(conn, args.window_id, args.bssid)
        if test_fp is None:
            print(f"Error: No fingerprint found for window {args.window_id}, BSSID {args.bssid}")
            sys.exit(1)

        if test_fp["measurement_id"] != args.measurement_id:
            print(f"Warning: Selected fingerprint belongs to measurement {test_fp['measurement_id']}, "
                f"not {args.measurement_id}. Continuing anyway.")

    # Extract metadata and vectors
    ref_meta = ref_fp.metadata
    test_meta = test_fp["metadata"]

    # Get sensor order – must be identical for both fingerprints
    sensor_order = ref_meta.get("sensor_order")
    if not sensor_order:
        # Fallback: use sensor_names JSON from the fingerprint
        sensor_order = ref_fp.sensor_names
    test_sensor_order = test_meta.get("sensor_order", test_fp["sensor_names"])
    if sensor_order != test_sensor_order:
        print("Error: Sensor order mismatch between reference and test fingerprints.")
        print(f"Ref: {sensor_order}")
        print(f"Test: {test_sensor_order}")
        sys.exit(1)

    # Number of subcarriers from metadata (or infer from vector length)
    n_subcarriers = ref_meta.get("n_subcarriers")
    if not n_subcarriers:
        # Infer: vector length = len(sensor_order) * n_subcarriers
        vec_len = len(np.frombuffer(ref_fp.vector, dtype=np.complex64))
        n_subcarriers = vec_len // len(sensor_order)
        if vec_len % len(sensor_order) != 0:
            print(f"Warning: Vector length {vec_len} not divisible by number of sensors {len(sensor_order)}")

    # Convert vectors to real numpy arrays (imag is zero)
    ref_vec = np.frombuffer(ref_fp.vector, dtype=np.complex64).real
    test_vec = np.frombuffer(test_fp["vector"], dtype=np.complex64).real

    if len(ref_vec) != len(test_vec):
        print(f"Error: Vector length mismatch: ref {len(ref_vec)} vs test {len(test_vec)}")
        sys.exit(1)

    # Split into per‑sensor profiles
    n_sensors = len(sensor_order)
    subcarrier_indices = np.arange(n_subcarriers)

    # Create a figure with one subplot per sensor
    fig, axes = plt.subplots(n_sensors, 1, figsize=(12, 3 * n_sensors), sharex=True)
    if n_sensors == 1:
        axes = [axes]

    for idx, sensor in enumerate(sensor_order):
        start = idx * n_subcarriers
        end = start + n_subcarriers
        ref_profile = ref_vec[start:end]
        test_profile = test_vec[start:end]

        ax = axes[idx]
        # Bar width and positions
        width = 0.35
        x = subcarrier_indices
        ax.bar(x - width/2, ref_profile, width, label=f"Reference (window {ref_fp.window_id})", color='green', alpha=0.7)
        ax.bar(x + width/2, test_profile, width, label=f"Selected (window {args.window_id})", color='blue', alpha=0.7)

        ax.set_title(f"Sensor: {sensor}")
        ax.set_ylabel("Amplitude")
        ax.legend()
        ax.grid(True, alpha=0.3)

    axes[-1].set_xlabel("Subcarrier index")
    fig.suptitle(f"CSI Amplitude Profile Comparison\nBSSID: {args.bssid} | Measurement ID: {args.measurement_id}", fontsize=14)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()