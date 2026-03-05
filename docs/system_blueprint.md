# System Blueprint

## 1. End-to-End Data Flow
1. `telemetry` collects raw metrics/events from infrastructure every 1-10 seconds.
2. `metrics_pipeline` validates schema, timestamps, unit-normalizes, and enriches with topology metadata.
3. Processed time-series is written to TSDB; high-priority events sent to event bus.
4. `thermal_model` and `power_model` run rolling inference/forecast jobs.
5. `ai_optimizer` computes ranked recommendations with confidence and risk score.
6. `alerts` emits incidents from model output + static policy violations.
7. `dashboard` visualizes state, incidents, and recommendations.

## 2. Shared Schemas

### MetricPoint
```json
{
  "ts": "2026-03-05T21:00:00Z",
  "site_id": "dc-west-1",
  "rack_id": "row-a-r12",
  "device_id": "srv-4421",
  "metric": "cpu_utilization",
  "value": 76.2,
  "unit": "percent",
  "tags": {"cluster": "inference-a", "role": "compute"}
}
```

### Recommendation
```json
{
  "id": "rec-01JXYZ",
  "ts": "2026-03-05T21:00:05Z",
  "type": "cooling_setpoint_adjustment",
  "target": {"zone": "aisle-a"},
  "action": {"delta_celsius": -1.5},
  "expected_impact": {"thermal_risk_delta": -22, "power_kw_delta": -14},
  "confidence": 0.84,
  "risk": "low",
  "requires_approval": true
}
```

## 3. Module Responsibilities

### telemetry
- Poll/subscribe to hardware and environmental sensors.
- Produce normalized `MetricPoint` messages to stream.
- Handle backoff, retries, local buffering.

### metrics_pipeline
- Schema validation and dead-letter routing.
- Unit harmonization (C/F, W/kW).
- Topology joins (rack -> row -> zone).
- Write to TSDB and event topic.

### thermal_model
- Inputs: inlet/outlet temp, CPU load, airflow proxy.
- Outputs: per-rack thermal risk score + 5/15/30 min forecast.
- Baseline approach: gradient boosting + temporal features.

### power_model
- Inputs: utilization, PSU telemetry, ambient conditions.
- Outputs: rack/site power forecast, PUE trend, efficiency anomalies.

### ai_optimizer
- Candidate generation:
  - rebalance workloads from high-risk racks
  - adjust cooling setpoints within policy limits
  - schedule power-capping windows
- Scoring objective:
  - minimize thermal risk + energy cost + SLA impact
- Constraints:
  - thermal upper bounds
  - power capacity limits
  - workload affinity/anti-affinity

### alerts
- Trigger from thresholds and model anomalies.
- Deduplicate and correlate by rack/zone/incident window.
- Escalation routes by severity.

### dashboard
- Live topology heatmap.
- Incident queue with ACK workflow.
- Recommendation panel with approve/reject and audit trail.

## 4. API Surface (MVP)
- `GET /api/v1/metrics/rack/{rack_id}`
- `GET /api/v1/thermal/risk`
- `GET /api/v1/recommendations`
- `POST /api/v1/recommendations/{id}/approve`
- `POST /api/v1/recommendations/{id}/reject`
- `GET /api/v1/incidents`

## 5. Delivery Plan

### Phase 0 (Week 1)
- Define schemas and synthetic telemetry generator.
- Stand up TSDB + event bus locally.

### Phase 1 (Weeks 2-4)
- Build ingestion + validation pipeline.
- Implement anomaly detector and thermal risk baseline.
- Ship incident feed + simple dashboard.

### Phase 2 (Weeks 5-8)
- Add power model and recommendation engine.
- Introduce approval workflow and policy checks.
- Run replay/simulation on historical windows.

### Phase 3 (Weeks 9-12)
- Guardrailed low-risk actuation for selected zones.
- Reliability hardening, SLO instrumentation, rollback playbooks.

## 6. Risk Controls
- Strict policy engine before actuation.
- Canary rollout by zone.
- Automatic rollback on threshold breach.
- Human-in-the-loop for medium/high-risk changes.
