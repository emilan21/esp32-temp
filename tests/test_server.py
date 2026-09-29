import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ServerApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.storage = tempfile.TemporaryDirectory(prefix="esp32-temp-test-")
        os.environ["DATA_DIR"] = cls.storage.name
        spec = importlib.util.spec_from_file_location(
            "room_sensor_app", ROOT / "server" / "app.py"
        )
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)
        cls.client = cls.module.app.test_client()

    @classmethod
    def tearDownClass(cls):
        cls.storage.cleanup()

    def setUp(self):
        with self.module.get_db_connection() as conn:
            conn.execute("DELETE FROM readings")

    def test_empty_state_and_health(self):
        self.assertEqual(self.client.get("/health").json, {"status": "ok"})
        self.assertEqual(self.client.get("/api/readings/latest").status_code, 404)
        self.assertEqual(self.client.get("/api/readings/latest-by-device").json, [])

    def test_post_converts_temperature_and_persists_reading(self):
        response = self.client.post(
            "/api/readings",
            json={"device_id": "living-room", "temp_c": "20", "humidity": "50"},
        )
        self.assertEqual(response.status_code, 200)
        reading = response.json["reading"]
        self.assertEqual(reading["temp_c"], 20.0)
        self.assertEqual(reading["temp_f"], 68.0)
        self.assertEqual(reading["humidity"], 50.0)
        self.assertEqual(
            self.client.get("/api/readings/latest").json["device_id"], "living-room"
        )

        history = self.client.get(
            "/api/readings/history?device_id=living-room&range=24h"
        )
        self.assertEqual(history.status_code, 200)
        self.assertEqual(len(history.json["points"]), 1)

    def test_latest_by_device_keeps_distinct_nodes(self):
        for device in ("living-room", "bedroom"):
            response = self.client.post(
                "/post", json={"device_id": device, "temp_f": 72, "humidity": 40}
            )
            self.assertEqual(response.status_code, 200)
        devices = self.client.get("/api/readings/latest-by-device").json
        self.assertEqual(
            {row["device_id"] for row in devices}, {"living-room", "bedroom"}
        )

    def test_rejects_invalid_json_and_sensor_values(self):
        self.assertEqual(
            self.client.post("/api/readings", data="not-json").status_code, 400
        )
        invalid = (
            {"temp_f": True, "humidity": 50},
            {"temp_f": "nan", "humidity": 50},
            {"temp_f": 72, "humidity": "inf"},
            {"temp_f": 72, "humidity": 101},
            {"temp_f": 72},
        )
        for payload in invalid:
            with self.subTest(payload=payload):
                self.assertEqual(
                    self.client.post("/api/readings", json=payload).status_code, 400
                )
        with self.module.get_db_connection() as conn:
            self.assertEqual(
                conn.execute("SELECT COUNT(*) FROM readings").fetchone()[0], 0
            )

    def test_history_requires_device_and_valid_range(self):
        self.assertEqual(self.client.get("/api/readings/history").status_code, 400)
        self.assertEqual(
            self.client.get("/api/readings/history?device_id=x&range=year").status_code,
            400,
        )


if __name__ == "__main__":
    unittest.main()
