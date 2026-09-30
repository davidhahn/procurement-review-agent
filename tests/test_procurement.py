import json
from pathlib import Path
import unittest

from fastapi.testclient import TestClient

from app.main import app
from app.procurement import ProcurementRequest, evaluate_policy, fixture_analysis

SAMPLE = json.loads(
    (Path(__file__).resolve().parents[1] / "examples/acme-request.json").read_text()
)


class ProcurementTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_example_routes_to_both_reviewers(self):
        response = self.client.post("/requests/analyze", json=SAMPLE)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["analysis_source"], "fixture")
        self.assertEqual(body["analysis"]["annual_cost_cents"], 120_000)
        self.assertEqual(body["status"], "requires_review")
        self.assertEqual(body["required_reviewers"], ["manager", "security"])
        self.assertEqual(body["rules_applied"], ["DEMO-SPEND-1", "DEMO-DATA-1"])
        self.assertTrue(body["missing_information"])

    def test_unsupported_input_has_no_canned_analysis(self):
        response = self.client.post("/requests/analyze", json={"request_text": "Buy another tool"})
        self.assertEqual(response.status_code, 422)
        self.assertIn("Only the Acme Analytics example", response.json()["detail"])
        self.assertNotIn("analysis", response.json())

    def test_missing_request_text_is_invalid(self):
        self.assertEqual(self.client.post("/requests/analyze", json={}).status_code, 422)

    def test_manager_threshold_is_strict_and_security_is_independent(self):
        analysis = fixture_analysis(ProcurementRequest(**SAMPLE))
        analysis.annual_cost_cents = 100_000
        self.assertEqual(evaluate_policy(analysis).required_reviewers, ["security"])
        analysis.annual_cost_cents = 100_001
        self.assertEqual(evaluate_policy(analysis).required_reviewers, ["manager", "security"])


if __name__ == "__main__":
    unittest.main()
