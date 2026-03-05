# Telemetry Module

This module handles infrastructure telemetry collection and normalization for the data center operations platform.

## Highlights
- Defined ingest expectations for multiple infra signal sources.
- Standardized output shape toward `MetricPoint`-style events.
- Outlined reliability improvements for buffering and retries.
- Integrates heterogeneous telemetry adapters.
- Emits normalized metric events for downstream processing.
- Reliability roadmap includes retry/backoff and local buffering.
- Schema pre-validation is part of ingestion hardening.
