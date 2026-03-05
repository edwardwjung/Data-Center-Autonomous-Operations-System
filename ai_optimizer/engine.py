from __future__ import annotations

from datetime import datetime
from typing import Dict, List
from uuid import uuid4

from schemas import RackState, Recommendation


class Optimizer:
    """Generates bounded recommendations from thermal and power signals."""

    def generate(self, racks: Dict[str, RackState]) -> List[Recommendation]:
        recommendations: List[Recommendation] = []
        now = datetime.utcnow()

        hot_racks = sorted(
            [rack for rack in racks.values() if rack.thermal_risk >= 65.0],
            key=lambda rack: rack.thermal_risk,
            reverse=True,
        )

        for rack in hot_racks[:4]:
            recommendations.append(
                Recommendation(
                    id=f"rec-{uuid4().hex[:10]}",
                    ts=now,
                    type="workload_rebalance",
                    target={"rack_id": rack.rack_id},
                    action={"cpu_migration_percent": min(35, int(rack.thermal_risk / 3))},
                    expected_impact={
                        "thermal_risk_delta": -min(30.0, rack.thermal_risk * 0.4),
                        "power_kw_delta": -max(0.3, rack.power_kw * 0.07),
                    },
                    confidence=0.78,
                    risk="low",
                    requires_approval=True,
                )
            )

        inefficient_racks = [rack for rack in racks.values() if rack.cooling_efficiency < 0.78]
        for rack in inefficient_racks[:3]:
            recommendations.append(
                Recommendation(
                    id=f"rec-{uuid4().hex[:10]}",
                    ts=now,
                    type="cooling_setpoint_adjustment",
                    target={"rack_id": rack.rack_id},
                    action={"delta_celsius": -1.0},
                    expected_impact={
                        "thermal_risk_delta": -12.0,
                        "power_kw_delta": -0.4,
                    },
                    confidence=0.71,
                    risk="medium",
                    requires_approval=True,
                )
            )

        return recommendations
