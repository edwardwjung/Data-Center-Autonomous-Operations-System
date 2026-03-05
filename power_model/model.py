from __future__ import annotations

from collections import defaultdict, deque
from typing import Deque, Dict

from schemas import RackState


class PowerModel:
    """Tracks rack power baselines and exposes anomaly score + PUE estimate."""

    def __init__(self, history_len: int = 40) -> None:
        self.power_history: Dict[str, Deque[float]] = defaultdict(lambda: deque(maxlen=history_len))
        self.last_pue: float = 1.0

    def score(self, racks: Dict[str, RackState]) -> float:
        total_it_kw = 0.0
        total_cooling_kw = 0.0

        for rack in racks.values():
            history = self.power_history[rack.rack_id]
            history.append(rack.power_kw)
            baseline = self._mean(history)
            if baseline <= 0:
                rack.power_anomaly_score = 0.0
            else:
                rack.power_anomaly_score = max(0.0, (rack.power_kw - baseline) / baseline)

            total_it_kw += rack.power_kw
            cooling_factor = max(0.1, 1.0 - rack.cooling_efficiency)
            total_cooling_kw += rack.power_kw * cooling_factor * 0.45

        facility_kw = total_it_kw + total_cooling_kw
        self.last_pue = facility_kw / total_it_kw if total_it_kw > 0 else 1.0
        return self.last_pue

    def _mean(self, values: Deque[float]) -> float:
        if not values:
            return 0.0
        return sum(values) / len(values)
