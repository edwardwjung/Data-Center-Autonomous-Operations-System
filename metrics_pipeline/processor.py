from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Dict, List

from schemas import MetricPoint, RackState


class MetricsProcessor:
    """Validates metric points and updates in-memory rack state."""

    ALLOWED_METRICS = {
        "cpu_utilization",
        "inlet_temp_c",
        "outlet_temp_c",
        "power_kw",
        "network_gbps",
        "cooling_efficiency",
    }

    def __init__(self) -> None:
        self.racks: Dict[str, RackState] = {}
        self.dead_letters: List[dict] = []
        self.metric_counts = defaultdict(int)

    def ingest(self, points: List[MetricPoint]) -> None:
        for point in points:
            if not self._valid(point):
                self.dead_letters.append({"ts": datetime.utcnow().isoformat(), "point": point})
                continue
            self.metric_counts[point.metric] += 1
            rack = self.racks.get(point.rack_id)
            if rack is None:
                rack = RackState(rack_id=point.rack_id)
                self.racks[point.rack_id] = rack
            self._apply_metric(rack, point)

    def _valid(self, point: MetricPoint) -> bool:
        if point.metric not in self.ALLOWED_METRICS:
            return False
        if point.site_id == "" or point.rack_id == "" or point.device_id == "":
            return False
        return True

    def _apply_metric(self, rack: RackState, point: MetricPoint) -> None:
        if point.metric == "cpu_utilization":
            rack.cpu_utilization = point.value
        elif point.metric == "inlet_temp_c":
            rack.inlet_temp_c = point.value
        elif point.metric == "outlet_temp_c":
            rack.outlet_temp_c = point.value
        elif point.metric == "power_kw":
            rack.power_kw = point.value
        elif point.metric == "network_gbps":
            rack.network_gbps = point.value
        elif point.metric == "cooling_efficiency":
            rack.cooling_efficiency = point.value

        rack.last_update = point.ts
