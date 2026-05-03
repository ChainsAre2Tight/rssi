import sqlite3
import json
from dataclasses import asdict

import my_types

from storage.physical_incidents import (
    load_physical_incident_groups,
    load_physical_signals_for_bssid,
)


def aggregate_physical_importance(
    signals: list[my_types.PhysicalSignal],
) -> my_types.Importance:
    severities = [my_types.Importance.from_str(s.importance) for s in signals]
    return max(severities, key=lambda s: s.rank)


class PhysicalModality(my_types.Modality):

    name = "physical"

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
            )

            if not signals:
                continue  # safety

            importance = self._compute_importance(signals)

            incident = self._build_incident(
                group,
                signals,
                importance,
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
        return load_physical_incident_groups(
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
    ):
        return load_physical_signals_for_bssid(
            conn,
            measurement_id,
            start_time_us,
            end_time_us,
            bssid,
        )

    def _compute_importance(
        self,
        signals: list[my_types.PhysicalSignal],
    ) -> my_types.Importance:

        return aggregate_physical_importance(signals)

    def _merge_intervals(
        self,
        signals: list[my_types.PhysicalSignal],
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
        signals: list[my_types.PhysicalSignal],
    ) -> list[my_types.LogicalWarning]:

        groups: dict[
            tuple[str, str, str, str | None],
            list[my_types.PhysicalSignal],
        ] = {}

        for s in signals:
            key = (s.detector, s.signal, s.importance, s.metadata_json)
            groups.setdefault(key, []).append(s)

        warnings: list[my_types.LogicalWarning] = []

        for (detector, signal, importance_str, metadata_json), group_signals in groups.items():

            importance = my_types.Importance.from_str(importance_str)

            occurrences = self._merge_intervals(group_signals)

            warnings.append(
                my_types.LogicalWarning(
                    detector=detector,
                    signal=signal,
                    importance=importance,
                    occurrences=occurrences,
                    metadata=json.loads(metadata_json) if metadata_json else {},
                )
            )

        return warnings

    def _build_incident(
        self,
        group: my_types.PhysicalIncidentGroup,
        signals: list[my_types.PhysicalSignal],
        importance: my_types.Importance,
    ) -> my_types.Incident:

        warnings = self._build_warnings(signals)

        # We return a structure compatible with LogicalIncident,
        # but with identity simplified (no SSID)
        return my_types.LogicalIncident(
            bssid=group.bssid,
            ssid=None,  # important: keep structure stable
            importance=importance,
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
        raise NotImplementedError("Physical modality does not support localization")

    def get_localization_report(
        self,
        conn: sqlite3.Connection,
        measurement_id: int,
        start_time_us: int,
        end_time_us: int,
        bssid: str,
    ) -> dict:
        raise NotImplementedError("Physical modality does not support localization")
