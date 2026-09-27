import csv
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from followup_experiment import run


def read_rows(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class FollowupExperimentTests(unittest.TestCase):
    def setUp(self):
        self.data = ROOT / "data"
        self.out = Path(tempfile.mkdtemp())

    def test_proposed_queue_matches_expected_counts(self):
        summary = run(self.data, self.out)
        self.assertEqual(summary["requests_evaluated"], 8)
        self.assertEqual(summary["baseline_actions"], 7)
        self.assertEqual(summary["proposed_actions"], 4)
        self.assertEqual(summary["proposed_reviews"], 3)
        self.assertEqual(summary["proposed_excludes"], 1)
        self.assertEqual(summary["duplicate_event_deliveries"], 4)
        self.assertEqual(summary["known_active_minutes_after_dedup"], 400)
        self.assertEqual(summary["logged_reminder_minutes_after_dedup"], 9)

    def test_edge_case_opt_out_is_excluded(self):
        summary = run(self.data, self.out)
        rows = read_rows(self.out / "triage_results.csv")
        opt_out = next(r for r in rows if r["request_id"] == "R012")
        self.assertEqual(opt_out["proposed"], "EXCLUDE")
        self.assertEqual(opt_out["reason"], "followup_not_allowed")
        self.assertEqual(summary["proposed_excludes"], 1)

    def test_no_action_input_is_valid(self):
        tmp = Path(tempfile.mkdtemp())
        for name in ["cases.csv", "requests.csv", "events.csv", "scenario.json"]:
            (tmp / name).write_text((self.data / name).read_text(), encoding="utf-8")
        rows = read_rows(tmp / "requests.csv")
        for r in rows:
            if r["item"] in {"fault_photo", "serial_number", "site_access"} and r["status"] == "pending":
                r["received_at"] = "2026-09-06T09:00+05:30"
        with (tmp / "requests.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows(rows)
        summary = run(tmp, self.out / "no_action")
        self.assertEqual(summary["proposed_actions"], 0)

    def test_changed_input_r024_moves_from_action_to_review(self):
        tmp = Path(tempfile.mkdtemp())
        for name in ["cases.csv", "requests.csv", "events.csv", "scenario.json"]:
            (tmp / name).write_text((self.data / name).read_text(), encoding="utf-8")
        rows = read_rows(tmp / "requests.csv")
        for r in rows:
            if r["request_id"] in {"R024", "R026"}:
                r["last_requested_at"] = "2026-09-06T12:00+05:30"
        with (tmp / "requests.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows(rows)
        summary = run(tmp, self.out / "changed")
        self.assertEqual(summary["proposed_actions"], 2)
        self.assertEqual(summary["proposed_reviews"], 5)
        result = read_rows(self.out / "changed" / "triage_results.csv")
        changed = [r for r in result if r["request_id"] in {"R024", "R026"}]
        self.assertTrue(all(r["proposed"] == "REVIEW" for r in changed))


if __name__ == "__main__":
    unittest.main()
