from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from fastapi import FastAPI

from dashboard.service import DataCenterOpsSystem

app = FastAPI(title="Data Center Autonomous Ops API", version="0.1.0")
ops = DataCenterOpsSystem()


def _rack_to_dict(rack: Any) -> Dict[str, Any]:
    return {
        "rack_id": rack.rack_id,
        "cpu_utilization": rack.cpu_utilization,
        "inlet_temp_c": rack.inlet_temp_c,
        "outlet_temp_c": rack.outlet_temp_c,
        "power_kw": rack.power_kw,
        "network_gbps": rack.network_gbps,
        "cooling_efficiency": rack.cooling_efficiency,
        "thermal_risk": rack.thermal_risk,
        "thermal_forecast_5m_c": rack.thermal_forecast_5m_c,
        "power_anomaly_score": rack.power_anomaly_score,
        "last_update": rack.last_update.isoformat() if rack.last_update else None,
    }


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


@app.post("/api/v1/tick")
def run_tick() -> Dict[str, Any]:
    snapshot = ops.tick()
    racks = [r for rid, r in snapshot.racks.items() if rid != "_site"]
    return {
        "racks_updated": len(racks),
        "incidents_total": len(snapshot.incidents),
        "recommendations_total": len(snapshot.recommendations),
    }


@app.get("/api/v1/thermal/risk")
def thermal_risk() -> List[Dict[str, Any]]:
    snapshot = ops.snapshot()
    racks = [snapshot.racks[rid] for rid in sorted(snapshot.racks.keys()) if rid != "_site"]
    return [_rack_to_dict(rack) for rack in racks]


@app.get("/api/v1/incidents")
def incidents(limit: int = 50) -> List[Dict[str, Any]]:
    rows = ops.recent_incidents(limit=limit)
    return [
        {
            "id": inc.id,
            "ts": inc.ts.isoformat(),
            "severity": inc.severity,
            "source": inc.source,
            "message": inc.message,
            "status": inc.status,
            "site_id": inc.site_id,
            "rack_id": inc.rack_id,
            "details": inc.details,
        }
        for inc in rows
    ]


@app.get("/api/v1/recommendations")
def recommendations(limit: int = 50) -> List[Dict[str, Any]]:
    rows = ops.recent_recommendations(limit=limit)
    return [
        {
            "id": rec.id,
            "ts": rec.ts.isoformat(),
            "type": rec.type,
            "target": rec.target,
            "action": rec.action,
            "expected_impact": rec.expected_impact,
            "confidence": rec.confidence,
            "risk": rec.risk,
            "requires_approval": rec.requires_approval,
        }
        for rec in rows
    ]
