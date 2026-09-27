#!/usr/bin/env python3
"""Dry-run experiment for missing-information follow-up triage.

Reads the supplied CSVs, compares a simple pending-list baseline with a
reconciled rule-based queue, and writes inspectable results. No messages are
sent and no network calls are made.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

IN_SCOPE_ITEMS = {"fault_photo", "serial_number", "site_access"}
CLOSED_STATUSES = {"completed", "cancelled", "scheduled"}


def parse_dt(value: str | None):
    return datetime.fromisoformat(value) if value else None


def load_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def classify(req, case, snapshot, min_gap_hours):
    """Return ACTION, REVIEW, or EXCLUDE with a reason."""
    status = case["status"]
    if status in CLOSED_STATUSES:
        return "EXCLUDE", f"case_status={status}"
    if req["followup_allowed"] != "1":
        return "EXCLUDE", "followup_not_allowed"
    if req["received_at"]:
        return "REVIEW", "request_received_but_status_is_pending"
    if not req["last_requested_at"]:
        return "REVIEW", "last_requested_at_missing"
    elapsed = (snapshot - parse_dt(req["last_requested_at"])).total_seconds() / 3600
    if elapsed < min_gap_hours:
        return "REVIEW", f"only_{elapsed:.1f}h_since_last_request"
    if not req["contact_address"] or not req["channel"]:
        return "REVIEW", "contact_or_channel_missing"
    return "ACTION", f"{elapsed:.1f}h_elapsed_and_item_not_received"


def baseline(req, case, snapshot, min_gap_hours):
    """Simple manual pending-list baseline: pending + open waiting_info + opt-in."""
    if req["item"] not in IN_SCOPE_ITEMS or req["status"] != "pending":
        return "OUT_OF_SCOPE"
    if case["status"] != "waiting_info":
        return "OUT_OF_SCOPE"
    if req["followup_allowed"] != "1":
        return "EXCLUDE"
    return "ACTION"  # baseline does not reconcile received/timing fields


def run(data_dir: Path, output_dir: Path, scenario_path: Path | None = None):
    scenario = json.loads((scenario_path or data_dir / "scenario.json").read_text(encoding="utf-8"))
    snapshot = parse_dt(scenario["snapshot_at"])
    gap = float(scenario["minimum_followup_gap_hours"])

    cases = {r["case_id"]: r for r in load_csv(data_dir / "cases.csv")}
    requests = load_csv(data_dir / "requests.csv")
    events = load_csv(data_dir / "events.csv")

    # Deduplicate exported event deliveries by stable event_id for effort/count metrics.
    unique_events = {}
    for row in events:
        unique_events.setdefault(row["event_id"], row)
    known_effort = sum(int(r["active_minutes"]) for r in unique_events.values() if r["active_minutes"])
    reminder_effort = sum(
        int(r["active_minutes"])
        for r in unique_events.values()
        if r["event_type"] == "reminder" and r["active_minutes"]
    )

    rows = []
    for req in requests:
        if req["item"] not in IN_SCOPE_ITEMS or req["status"] != "pending":
            continue
        case = cases[req["case_id"]]
        b = baseline(req, case, snapshot, gap)
        if b == "OUT_OF_SCOPE":
            continue
        p, reason = classify(req, case, snapshot, gap)
        rows.append({
            "request_id": req["request_id"],
            "case_id": req["case_id"],
            "item": req["item"],
            "baseline": b,
            "proposed": p,
            "reason": reason,
            "last_requested_at": req["last_requested_at"],
            "received_at": req["received_at"],
        })

    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "triage_results.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "snapshot_at": scenario["snapshot_at"],
        "requests_evaluated": len(rows),
        "baseline_actions": sum(r["baseline"] == "ACTION" for r in rows),
        "proposed_actions": sum(r["proposed"] == "ACTION" for r in rows),
        "proposed_reviews": sum(r["proposed"] == "REVIEW" for r in rows),
        "proposed_excludes": sum(r["proposed"] == "EXCLUDE" for r in rows),
        "baseline_to_action_reduction": round(
            (sum(r["baseline"] == "ACTION" for r in rows) - sum(r["proposed"] == "ACTION" for r in rows))
            / max(1, sum(r["baseline"] == "ACTION" for r in rows)), 4
        ),
        "event_rows": len(events),
        "unique_event_ids": len(unique_events),
        "duplicate_event_deliveries": len(events) - len(unique_events),
        "known_active_minutes_after_dedup": known_effort,
        "logged_reminder_minutes_after_dedup": reminder_effort,
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data"))
    parser.add_argument("--output", type=Path, default=Path("output"))
    parser.add_argument("--scenario", type=Path, default=None)
    args = parser.parse_args()
    summary = run(args.data, args.output, args.scenario)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
