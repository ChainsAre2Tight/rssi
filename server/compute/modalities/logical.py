from dataclasses import asdict
import sqlite3
import json

import my_types

from storage.localization_jobs import count_localization_jobs, insert_localization_jobs
from storage.localization_results import load_localization_results
from storage.logical_incidents import load_logical_incident_groups, load_signals_for_identity
from storage.windows import get_windows_in_range, get_windows_with_observation_for_bssid


def aggregate_severity(signals: list[my_types.LogicalSignal]) -> my_types.Severity:
    severities = [my_types.Severity.from_str(s.severity) for s in signals]
    return max(severities, key=lambda s: s.rank)


class LogicalModality(my_types.Modality):

    name = "logical"

    def build_incidents(
        self,
        conn: sqlite3.Connection,
        measurement_id: int,
        start_time_us: int,
        end_time_us: int,
    ) -> list[my_types.Incident]:

        groups = self._load_groups(
            conn,
            measurement_id,
            start_time_us,
            end_time_us,
        )

        incidents: list[my_types.Incident] = []

        for group in groups:

            signals = self._load_signals(
                conn,
                measurement_id,
                start_time_us,
                end_time_us,
                group.bssid,
                group.ssid,
            )

            severity = self._compute_severity(signals)

            incident = self._build_incident(
                group,
                signals,
                severity,
            )

            incidents.append(incident)

        return incidents

    def _load_groups(
        self,
        conn,
        measurement_id,
        start_time_us,
        end_time_us,
    ):
        return load_logical_incident_groups(
            conn,
            measurement_id,
            start_time_us,
            end_time_us,
        )

    def _load_signals(
        self,
        conn,
        measurement_id,
        start_time_us,
        end_time_us,
        bssid,
        ssid,
    ):
        return load_signals_for_identity(
            conn,
            measurement_id,
            start_time_us,
            end_time_us,
            bssid,
            ssid,
        )

    def _compute_severity(
        self,
        signals: list[my_types.LogicalSignal],
    ) -> my_types.Severity:

        return aggregate_severity(signals)
    
    def _merge_intervals(
        self,
        signals: list[my_types.LogicalSignal],
    ) -> list[my_types.LogicalWarningOccurrence]:

        intervals = sorted(
            [(s.start_time_us, s.end_time_us) for s in signals]
        )

        merged: list[my_types.LogicalWarningOccurrence] = []

        cur_start, cur_end = intervals[0]

        for start, end in intervals[1:]:

            if start <= cur_end:
                cur_end = max(cur_end, end)
            else:
                merged.append(
                    my_types.LogicalWarningOccurrence(
                        start_time_us=cur_start,
                        end_time_us=cur_end,
                    )
                )
                cur_start, cur_end = start, end

        merged.append(
            my_types.LogicalWarningOccurrence(
                start_time_us=cur_start,
                end_time_us=cur_end,
            )
        )

        return merged

    def _build_warnings(
        self,
        signals: list[my_types.LogicalSignal],
    ) -> list[my_types.LogicalWarning]:

        groups: dict[tuple[str, str, str, str], list[my_types.LogicalSignal]] = {}

        for s in signals:
            key = (s.detector, s.signal, s.severity, s.metadata_json)
            groups.setdefault(key, []).append(s)

        warnings: list[my_types.LogicalWarning] = []

        for (detector, signal, severity_str, metadata_json), group_signals in groups.items():

            severity = my_types.Severity.from_str(severity_str)

            occurrences = self._merge_intervals(group_signals)

            warnings.append(
                my_types.LogicalWarning(
                    detector=detector,
                    signal=signal,
                    severity=severity,
                    occurrences=occurrences,
                    metadata=json.loads(metadata_json),
                )
            )

        return warnings

    def _build_incident(
        self,
        group: my_types.LogicalIncidentGroup,
        signals: list[my_types.LogicalSignal],
        severity: my_types.Severity,
    ) -> my_types.LogicalIncident:

        warnings = self._build_warnings(signals)

        return my_types.LogicalIncident(
            bssid=group.bssid,
            ssid=group.ssid,
            severity=severity,
            start_time_us=group.first_seen_us,
            end_time_us=group.last_seen_us,
            warnings=warnings,
        )

    def enqueue_localization_jobs(
        self,
        conn: sqlite3.Connection,
        measurement_id: int,
        start_time_us: int,
        end_time_us: int,
        bssid: str,
    ) -> dict:

        window_ids = get_windows_in_range(
            conn,
            measurement_id,
            start_time_us,
            end_time_us,
            0,
        )

        valid_windows = get_windows_with_observation_for_bssid(
            conn,
            window_ids,
            bssid,
        )

        jobs = [(w, bssid) for w in valid_windows]

        inserted, ignored = insert_localization_jobs(
            conn,
            measurement_id,
            jobs,
        )

        skipped = len(window_ids) - len(valid_windows)

        return {
            "measurement_id": measurement_id,
            "modality": self.name,
            "bssid": bssid,
            "windows": len(window_ids),
            "jobs_created": inserted,
            "jobs_ignored": ignored,
            "windows_without_observation": skipped,
        }

    def get_localization_report(
        self,
        conn: sqlite3.Connection,
        measurement_id: int,
        start_time_us: int,
        end_time_us: int,
        bssid: str,
    ) -> dict:

        window_ids = get_windows_in_range(
            conn,
            measurement_id,
            start_time_us,
            end_time_us,
            0
        )

        counts = count_localization_jobs(
            conn,
            measurement_id,
            window_ids,
            bssid,
        )

        results = load_localization_results(
            conn,
            measurement_id,
            window_ids,
            bssid,
        )

        return {
            "measurement_id": measurement_id,
            "modality": self.name,
            "bssid": bssid,
            "completed": counts.get("done", 0),
            "pending": counts.get("pending", 0),
            "processing": counts.get("processing", 0),
            "failed": counts.get("error", 0),
            "locations": [asdict(r) for r in results],
        }

if __name__ == "__main__":

    import json
    import config
    import storage

    MEASUREMENT_ID = config.MEASUREMENT_ID

    START_TIME_US = 0
    END_TIME_US = 1775679780000000

    modality = LogicalModality()

    with storage.Session() as conn:

        incidents = modality.build_incidents(
            conn=conn,
            measurement_id=MEASUREMENT_ID,
            start_time_us=START_TIME_US,
            end_time_us=END_TIME_US,
        )

    print(f"Incidents found: {len(incidents)}\n")

    # for incident in incidents:
    #     print(json.dumps(incident.to_dict(), indent=2))

    print(json.dumps(incidents[0].to_dict(), indent=2))

        
