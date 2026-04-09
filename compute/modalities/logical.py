import sqlite3

import my_types

from storage.logical_incidents import load_logical_incident_groups, load_signals_for_identity


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

    def _build_incident(
        self,
        group: my_types.LogicalIncidentGroup,
        signals: list[my_types.LogicalSignal],
        severity: my_types.Severity,
    ) -> my_types.LogicalIncident:

        return my_types.LogicalIncident(
            bssid=group.bssid,
            ssid=group.ssid,
            severity=severity,
            start_time_us=group.first_seen_us,
            end_time_us=group.last_seen_us,
            signals=signals,
            # signals=[],
        )


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

        
