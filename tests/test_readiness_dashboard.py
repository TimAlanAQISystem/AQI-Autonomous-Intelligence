from __future__ import annotations

import json
from pathlib import Path

from tools.build_readiness_dashboard import _build_html, _list_readiness_runs


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_dashboard_lists_runs_and_renders_status(tmp_path: Path) -> None:
    _write_json(
        tmp_path / "governance_runs" / "readiness" / "20260722-100000" / "readiness_decision.json",
        {
            "generated_at_utc": "2026-07-22T10:00:00+00:00",
            "overall_status": "READY",
            "pass_count": 7,
            "conditional_count": 0,
            "fail_count": 0,
        },
    )
    _write_json(
        tmp_path / "governance_runs" / "readiness" / "20260722-110000" / "readiness_decision.json",
        {
            "generated_at_utc": "2026-07-22T11:00:00+00:00",
            "overall_status": "NOT_READY",
            "pass_count": 5,
            "conditional_count": 1,
            "fail_count": 1,
        },
    )

    runs = _list_readiness_runs(tmp_path, limit=10)
    assert len(runs) == 2

    html = _build_html(runs)
    assert "AQI V-8 Readiness Dashboard" in html
    assert "NOT_READY" in html
    assert "READY" in html
