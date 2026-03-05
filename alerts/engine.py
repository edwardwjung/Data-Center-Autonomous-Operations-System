from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List
from uuid import uuid4

from schemas import Incident, RackState


class AlertEngine:
    """Threshold and anomaly based incident generation with short dedupe window."""

    def __init__(self, dedupe_minutes: int = 10) -> None:
        self.dedupe_window = timedelta(minutes=dedupe_minutes)
        self._active_keys: Dict[str, datetime] = {}

    def detect(self, site_id: str, racks: Dict[str, RackState]) -> List[Incident]:
        now = datetime.utcnow()
        incidents: List[Incident] = []

        for rack in racks.values():
            candidates = []
            if rack.thermal_risk >= 80:
                candidates.append(("critical", "thermal_model", "Critical thermal risk"))
            elif rack.thermal_risk >= 65:
                candidates.append(("high", "thermal_model", "Elevated thermal risk"))

            if rack.power_anomaly_score >= 0.25:
                candidates.append(("medium", "power_model", "Power anomaly detected"))

            for severity, source, message in candidates:
                key = f"{rack.rack_id}:{source}:{severity}:{message}"
                last_seen = self._active_keys.get(key)
                if last_seen is not None and (now - last_seen) < self.dedupe_window:
                    continue
                self._active_keys[key] = now
                incidents.append(
                    Incident(
                        id=f"inc-{uuid4().hex[:10]}",
                        ts=now,
                        severity=severity,
                        source=source,
                        message=message,
                        status="open",
                        site_id=site_id,
                        rack_id=rack.rack_id,
                        details={
                            "thermal_risk": round(rack.thermal_risk, 2),
                            "power_anomaly_score": round(rack.power_anomaly_score, 3),
                            "forecast_5m_c": round(rack.thermal_forecast_5m_c, 2),
                        },
                    )
                )

        return incidents
