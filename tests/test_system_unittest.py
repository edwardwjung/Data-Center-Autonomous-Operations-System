import unittest

from dashboard.service import DataCenterOpsSystem


class DataCenterOpsTests(unittest.TestCase):
    def test_tick_creates_rack_state(self) -> None:
        system = DataCenterOpsSystem(rack_count=3)
        snapshot = system.tick()

        racks = [r for rid, r in snapshot.racks.items() if rid != "_site"]
        self.assertEqual(len(racks), 3)
        self.assertTrue(all(rack.last_update is not None for rack in racks))

    def test_thermal_risk_is_bounded(self) -> None:
        system = DataCenterOpsSystem(rack_count=4)
        for _ in range(5):
            snapshot = system.tick()

        racks = [r for rid, r in snapshot.racks.items() if rid != "_site"]
        self.assertTrue(all(0.0 <= rack.thermal_risk <= 100.0 for rack in racks))

    def test_recommendations_shape(self) -> None:
        system = DataCenterOpsSystem(rack_count=6)
        for _ in range(8):
            snapshot = system.tick()

        if snapshot.recommendations:
            rec = snapshot.recommendations[-1]
            self.assertTrue(rec.id.startswith("rec-"))
            self.assertGreaterEqual(rec.confidence, 0.0)
            self.assertLessEqual(rec.confidence, 1.0)
            self.assertIn(rec.risk, {"low", "medium", "high"})


if __name__ == "__main__":
    unittest.main()
