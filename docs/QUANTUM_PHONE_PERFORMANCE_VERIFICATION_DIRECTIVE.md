# Directive: Quantum Phone Performance Verification

When working on Alan's voice or telephony stack, always follow this directive.

## 1. Review governance archives

1. Read the latest sessions in `RESTART_RECOVERY_GUIDE_VII.md` (RRG), focusing on phone-related changes (Sessions 13-20+).
2. Confirm how quantum routing, admissibility, and evidence binding are currently enforced.

## 2. Inspect telephone performance metrics

1. Use `governance_runs/conversation_performance/<call_id>/summary.json` and per-turn artifacts to check:
2. ASR, QPC/LLM/tools, TTS, and total latency.
3. `route_class` (`fast` vs `heavy`) and `latency_class` (`fast`, `acceptable`, `slow`).
4. Verify p95/p99 latencies meet or improve the SLOs defined in `CONVERSATION_PERFORMANCE_LAYER.md`.
5. Run SLO evaluation and persist governance evidence:

```bash
python tools/run_slo_evaluations.py --latest --fail-on-violation
```

6. SLO pass criteria are evaluated from `aqi/core/slo_config.py` and include:
	- `ASR_P95`, `QPC_P95`, `TTS_P95`, `TURN_P95`, `TURN_P99`
	- `MAX_SLOW_TURNS`, `MAX_HEAVY_SLOW_TURNS`
7. Evaluation artifacts must exist at:
	- `governance_runs/slo_evaluations/<call_id>/evaluation.json`
	- `governance_runs/slo_evaluations/<call_id>/report.txt`

## 3. Evaluate Alan's voice behavior

1. Cross-check actual call behavior against `IDEAL_ALAN_CALL_BLUEPRINT.md`:
2. pre-call warmup
3. fast vs heavy path usage
4. slow-turn bridge lines
5. repair strategies and turn-taking
6. Ensure spoken output (TTS) matches bridge and response logic in code.

## 4. Confirm quantum superiority over legacy paths

1. Ensure all active dial surfaces (`outbound_controller.py`, `aqi_agent_x.py`, `telephony_resilience.py`) are using:
2. `run_quantum_twilio_call(...)`
3. `QuantumScheduler`
4. `AdmissibilityGate`
5. `EvidenceRegistry`
6. Legacy/non-quantum paths must remain env-gated escape hatches only, never defaults.

## 5. Enforce governance and CI invariants

1. Run:

```bash
python tools/negproof_quantum_routing_audit.py --root . --scope aqi,aqi_agent_x.py,telephony_resilience.py,outbound_controller.py --strict
```

2. Do not ship changes unless all are true:
3. strict audit reports `violations=0`
4. all tests pass
5. `RESTART_RECOVERY_GUIDE_VII.md` is updated with a new session documenting changes and their impact on quantum phone performance.
