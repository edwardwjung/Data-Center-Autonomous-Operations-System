from __future__ import annotations

from collections import deque
from dataclasses import fields
from datetime import datetime
from typing import Deque, Dict, List

from ai_optimizer import Optimizer
from alerts import AlertEngine
from metrics_pipeline import MetricsProcessor
from power_model import PowerModel
from schemas import Incident, PipelineSnapshot, Recommendation, RackState
from telemetry import TelemetrySimulator
from thermal_model import ThermalRiskModel


class DataCenterOpsSystem:
    """Coordinates telemetry ingestion, model scoring, optimization, and alerts."""

    def __init__(self, site_id: str = "dc-west-1", rack_count: int = 8) -> None:
        self.site_id = site_id
        self.simulator = TelemetrySimulator(site_id=site_id, rack_count=rack_count)
        self.processor = MetricsProcessor()
        self.thermal_model = ThermalRiskModel()
        self.power_model = PowerModel()
        self.optimizer = Optimizer()
        self.alert_engine = AlertEngine()

        self.incidents: Deque[Incident] = deque(maxlen=500)
        self.recommendations: Deque[Recommendation] = deque(maxlen=500)

    def tick(self) -> PipelineSnapshot:
        points = self.simulator.tick()
        self.processor.ingest(points)
        racks = self.processor.racks

        for rack in racks.values():
            self.thermal_model.score(rack)
        pue = self.power_model.score(racks)

        new_recs = self.optimizer.generate(racks)
        new_incidents = self.alert_engine.detect(self.site_id, racks)

        self.recommendations.extend(new_recs)
        self.incidents.extend(new_incidents)

        snapshot = self.snapshot()
        snapshot.racks["_site"] = RackState(
            rack_id="_site",
            power_kw=sum(r.power_kw for r in racks.values()),
            cooling_efficiency=max(0.0, min(1.0, 2.0 - pue)),
            last_update=datetime.utcnow(),
        )
        return snapshot

    def snapshot(self) -> PipelineSnapshot:
        racks_copy: Dict[str, RackState] = {
            rid: RackState(**{field.name: getattr(rack, field.name) for field in fields(RackState)})
            for rid, rack in self.processor.racks.items()
        }
        return PipelineSnapshot(
            racks=racks_copy,
            incidents=list(self.incidents),
            recommendations=list(self.recommendations),
        )

    def recent_incidents(self, limit: int = 50) -> List[Incident]:
        return list(self.incidents)[-limit:]

    def recent_recommendations(self, limit: int = 50) -> List[Recommendation]:
        return list(self.recommendations)[-limit:]
