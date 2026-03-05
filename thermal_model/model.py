from __future__ import annotations

from collections import defaultdict, deque
from typing import Deque, Dict

from schemas import RackState


class ThermalRiskModel:
    """Simple thermal risk score and short-horizon forecast model."""

    def __init__(self, history_len: int = 30) -> None:
        self.inlet_history: Dict[str, Deque[float]] = defaultdict(lambda: deque(maxlen=history_len))
        self.outlet_history: Dict[str, Deque[float]] = defaultdict(lambda: deque(maxlen=history_len))

    def score(self, rack: RackState) -> None:
        in_hist = self.inlet_history[rack.rack_id]
        out_hist = self.outlet_history[rack.rack_id]
        in_hist.append(rack.inlet_temp_c)
        out_hist.append(rack.outlet_temp_c)

        inlet_baseline = self._mean(in_hist)
        outlet_baseline = self._mean(out_hist)

        inlet_delta = max(0.0, rack.inlet_temp_c - inlet_baseline)
        outlet_delta = max(0.0, rack.outlet_temp_c - outlet_baseline)

        risk = (
            (rack.cpu_utilization / 100.0) * 30.0
            + (inlet_delta * 8.0)
            + (outlet_delta * 6.0)
            + (max(0.0, 0.9 - rack.cooling_efficiency) * 50.0)
        )

        rack.thermal_risk = max(0.0, min(100.0, risk))
        trend = self._trend(out_hist)
        rack.thermal_forecast_5m_c = max(rack.outlet_temp_c, rack.outlet_temp_c + trend * 5.0)

    def _mean(self, values: Deque[float]) -> float:
        if not values:
            return 0.0
        return sum(values) / len(values)

    def _trend(self, values: Deque[float]) -> float:
        if len(values) < 2:
            return 0.0
        return (values[-1] - values[0]) / max(1, len(values) - 1)
