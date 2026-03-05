from __future__ import annotations

import argparse
import json
from time import sleep

from dashboard.service import DataCenterOpsSystem


def main() -> None:
    parser = argparse.ArgumentParser(description="Run data center ops simulation loop")
    parser.add_argument("--ticks", type=int, default=10, help="Number of simulation ticks")
    parser.add_argument("--interval", type=float, default=0.0, help="Seconds between ticks")
    args = parser.parse_args()

    system = DataCenterOpsSystem()
    for idx in range(args.ticks):
        snapshot = system.tick()
        hot = sorted(
            [rack for rack in snapshot.racks.values() if rack.rack_id != "_site"],
            key=lambda rack: rack.thermal_risk,
            reverse=True,
        )[:3]
        payload = {
            "tick": idx + 1,
            "top_hot_racks": [
                {
                    "rack_id": rack.rack_id,
                    "thermal_risk": round(rack.thermal_risk, 2),
                    "outlet_temp_c": round(rack.outlet_temp_c, 2),
                }
                for rack in hot
            ],
            "incidents_total": len(snapshot.incidents),
            "recommendations_total": len(snapshot.recommendations),
        }
        print(json.dumps(payload))
        if args.interval > 0:
            sleep(args.interval)


if __name__ == "__main__":
    main()
