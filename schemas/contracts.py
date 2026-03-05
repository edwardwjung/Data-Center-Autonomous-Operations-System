from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class MetricPoint:
    ts: datetime
    site_id: str
    rack_id: str
    device_id: str
    metric: str
    value: float
    unit: str
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class Incident:
    id: str
    ts: datetime
    severity: str
    source: str
    message: str
    status: str
    site_id: str
    rack_id: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Recommendation:
    id: str
    ts: datetime
    type: str
    target: Dict[str, Any]
    action: Dict[str, Any]
    expected_impact: Dict[str, float]
    confidence: float
    risk: str
    requires_approval: bool


@dataclass
class RackState:
    rack_id: str
    cpu_utilization: float = 0.0
    inlet_temp_c: float = 0.0
    outlet_temp_c: float = 0.0
    power_kw: float = 0.0
    network_gbps: float = 0.0
    cooling_efficiency: float = 0.0
    thermal_risk: float = 0.0
    thermal_forecast_5m_c: float = 0.0
    power_anomaly_score: float = 0.0
    last_update: datetime | None = None


@dataclass
class PipelineSnapshot:
    racks: Dict[str, RackState]
    incidents: List[Incident]
    recommendations: List[Recommendation]
