# reporter.py
"""
Scenario reporter – human-readable and machine-readable outputs.

Writes JSON reports with:
  - Scenario spec
  - Validation result (passed/violations)
  - Trace summary
"""

from pathlib import Path
import json
from datetime import datetime


class ScenarioReporter:
    """Writes Neg-Proof scenario reports to disk."""

    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def report(self, spec: dict, traces: list, result: dict):
        """
        Write a JSON report for a scenario run.

        Args:
            spec: Scenario specification.
            traces: Full event trace.
            result: Validation result with 'passed' and 'violations'.
        """
        name = spec.get("name", "unnamed_scenario")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = self.output_dir / f"{name}_{timestamp}_report.json"

        payload = {
            "timestamp": timestamp,
            "scenario": name,
            "profile": spec.get("scenario_profile", "unknown"),
            "description": spec.get("description", ""),
            "result": result,
            "trace_summary": self._summarize_traces(traces),
            "trace_count": len(traces),
        }

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        return out_path

    def _summarize_traces(self, traces: list) -> list:
        """Create a condensed summary of traces for the report."""
        summary = []
        for ev in traces:
            summary.append({
                "t": ev["t"],
                "event": ev["event"],
                "key_data": {k: v for k, v in ev.get("data", {}).items()
                             if k in ("turn_state", "energy_db", "delay_ms",
                                      "intent_to_speak", "merchant_floor",
                                      "transcript", "error")},
            })
        return summary

    def print_result(self, spec: dict, result: dict):
        """Print a human-readable result to stdout."""
        name = spec.get("name", "unnamed")
        status = "PASS" if result["passed"] else "FAIL"
        print(f"  [{status}] {name}")
        if not result["passed"]:
            for v in result.get("violations", []):
                vtype = v.get("type", "unknown")
                msg = v.get("message", v.get("details", {}).get("message", ""))
                print(f"        -> {vtype}: {msg}")
