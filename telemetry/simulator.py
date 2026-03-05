from __future__ import annotations

import random
from datetime import datetime
from typing import Iterable, List

from schemas import MetricPoint


class TelemetrySimulator:
    """Generates synthetic rack telemetry with occasional anomalies."""

    def __init__(self, site_id: str = "dc-west-1", rack_count: int = 8, seed: int = 7) -> None:
        self.site_id = site_id
        self.rack_ids = [f"row-a-r{idx:02d}" for idx in range(1, rack_count + 1)]
        self._rng = random.Random(seed)

    def tick(self) -> List[MetricPoint]:
        now = datetime.utcnow()
        points: List[MetricPoint] = []
        for rack_id in self.rack_ids:
            cpu = self._base(55.0, 18.0)
            inlet = self._base(24.0, 2.0)
            outlet = inlet + self._base(10.0, 2.5)
            power = self._base(6.0, 1.4) + (cpu / 100.0) * 4.0
            net = self._base(4.0, 1.5)
            cooling = self._base(0.84, 0.05)

            if self._rng.random() < 0.06:
                inlet += self._rng.uniform(4.0, 8.0)
                outlet += self._rng.uniform(7.0, 12.0)
                power += self._rng.uniform(1.0, 3.0)

            metrics = {
                "cpu_utilization": (max(0.0, min(cpu, 100.0)), "percent"),
                "inlet_temp_c": (inlet, "celsius"),
                "outlet_temp_c": (outlet, "celsius"),
                "power_kw": (max(0.0, power), "kw"),
                "network_gbps": (max(0.0, net), "gbps"),
                "cooling_efficiency": (max(0.0, min(cooling, 1.0)), "ratio"),
            }

            for metric_name, (value, unit) in metrics.items():
                points.append(
                    MetricPoint(
                        ts=now,
                        site_id=self.site_id,
                        rack_id=rack_id,
                        device_id=f"{rack_id}-srv-01",
                        metric=metric_name,
                        value=float(value),
                        unit=unit,
                        tags={"source": "simulator"},
                    )
                )

        return points

    def _base(self, mean: float, spread: float) -> float:
        return self._rng.gauss(mean, spread)


def stream_ticks(simulator: TelemetrySimulator, ticks: int) -> Iterable[List[MetricPoint]]:
    for _ in range(ticks):
        yield simulator.tick()
