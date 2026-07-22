#!/usr/bin/env python3
"""Build a static readiness dashboard from governance artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _list_readiness_runs(root: Path, limit: int) -> list[tuple[str, dict[str, Any], Path]]:
    base = root / "governance_runs" / "readiness"
    if not base.exists():
        return []

    runs: list[tuple[str, dict[str, Any], Path]] = []
    for path in sorted(base.glob("*/readiness_decision.json"), reverse=True):
        try:
            payload = _load_json(path)
            runs.append((path.parent.name, payload, path.parent))
        except Exception:
            continue
        if len(runs) >= limit:
            break
    return runs


def _status_badge(status: str) -> str:
    cls = "status-unknown"
    if status == "READY":
        cls = "status-ready"
    elif status == "NOT_READY":
        cls = "status-not-ready"
    return f'<span class="status-badge {cls}">{status}</span>'


def _build_html(runs: list[tuple[str, dict[str, Any], Path]]) -> str:
    latest = runs[0][1] if runs else {"overall_status": "UNKNOWN", "pass_count": 0, "conditional_count": 0, "fail_count": 0}
    latest_status = str(latest.get("overall_status", "UNKNOWN"))

    table_rows: list[str] = []
    for run_id, payload, run_dir in runs:
        status = str(payload.get("overall_status", "UNKNOWN"))
        passed = int(payload.get("pass_count", 0) or 0)
        conditional = int(payload.get("conditional_count", 0) or 0)
        failed = int(payload.get("fail_count", 0) or 0)
        generated = str(payload.get("generated_at_utc", ""))
        md_rel = run_dir.as_posix() + "/readiness_decision.md"
        table_rows.append(
            "<tr>"
            f"<td>{run_id}</td>"
            f"<td>{generated}</td>"
            f"<td>{_status_badge(status)}</td>"
            f"<td>{passed}</td>"
            f"<td>{conditional}</td>"
            f"<td>{failed}</td>"
            f"<td><a href=\"../../{md_rel}\">report</a></td>"
            "</tr>"
        )

    rows = "\n".join(table_rows) if table_rows else "<tr><td colspan=\"7\">No readiness runs found.</td></tr>"

    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>AQI V-8 Readiness Dashboard</title>
  <link rel=\"stylesheet\" href=\"static/styles.css\" />
</head>
<body>
  <main class=\"wrap\">
    <section class=\"hero\">
      <h1>AQI V-8 Readiness Dashboard</h1>
      <p>Operational readiness trend and gate outcome history.</p>
      <div class=\"latest\">
        <div>Current Status: {_status_badge(latest_status)}</div>
        <div>PASS: {int(latest.get('pass_count', 0) or 0)}</div>
        <div>CONDITIONAL: {int(latest.get('conditional_count', 0) or 0)}</div>
        <div>FAIL: {int(latest.get('fail_count', 0) or 0)}</div>
      </div>
    </section>

    <section>
      <h2>Recent Runs</h2>
      <table>
        <thead>
          <tr>
            <th>Run ID</th>
            <th>Generated UTC</th>
            <th>Status</th>
            <th>PASS</th>
            <th>CONDITIONAL</th>
            <th>FAIL</th>
            <th>Details</th>
          </tr>
        </thead>
        <tbody>
          {rows}
        </tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build static AQI readiness dashboard")
    parser.add_argument("--limit", type=int, default=20, help="Number of runs to include")
    parser.add_argument(
        "--out-dir",
        default="governance_runs/readiness_dashboard",
        help="Output directory for dashboard assets",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    runs = _list_readiness_runs(ROOT, limit=max(1, args.limit))

    out_dir = ROOT / args.out_dir
    static_dir = out_dir / "static"
    static_dir.mkdir(parents=True, exist_ok=True)

    html = _build_html(runs)
    (out_dir / "index.html").write_text(html, encoding="utf-8")

    css_src = ROOT / "aqi" / "dashboard" / "static" / "styles.css"
    css_dst = static_dir / "styles.css"
    if css_src.exists():
        css_dst.write_text(css_src.read_text(encoding="utf-8"), encoding="utf-8")

    print("Readiness dashboard generated")
    print(f"runs_included={len(runs)}")
    print(f"dashboard={out_dir / 'index.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
