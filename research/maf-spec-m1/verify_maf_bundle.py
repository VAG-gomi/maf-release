#!/usr/bin/env python3
"""Production/evidence verifier for the completed SPEC-M1 MAF bundle.

This verifier is intentionally read-only with respect to scientific artifacts.
It does not import or execute the training runner. It validates the committed
outputs, their cross-artifact relationships, and the authored transmission
contract.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEEDS = list(range(2000, 2030))
METHODS = ["V-FULL", "V-A0", "V-SOFT", "V-ORAC", "B-POOL", "B-ENVNN", "B-MIXED", "B-IRML"]
BASELINES = ["B-POOL", "B-ENVNN", "B-MIXED", "B-IRML"]
LIVE_CHANNEL = {"V-FULL", "V-SOFT", "V-ORAC"}
NO_CHANNEL = {"V-A0", *BASELINES}
T2_COLUMNS = ["seed", "variant_or_baseline", "rmse_holdout", "m_psi", "m_dauroc"]
SUMMARY_STATS = [
    "g0a_pass_scale",
    "g0b_lambda1_chosen",
    "g0b_best_correlation",
    "p1_vfull_rmse_median",
    "p1_best_baseline_name",
    "p1_best_baseline_rmse_median",
    "p1_relative_reduction",
    "p2_mpsi_median",
    "p3_mdauroc_median",
    "k1_gap_percent",
    "k2_gap_percent",
    "k4_vorac_mpsi_median",
    "verdict_label",
]


def fail(message: str) -> None:
    raise AssertionError(message)


def finite(value: object, label: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        fail(f"{label} is not numeric: {value!r}")
        raise exc
    if not math.isfinite(out):
        fail(f"{label} is not finite: {value!r}")
    return out


def close(a: object, b: object, label: str, rel: float = 1e-12, abs_tol: float = 1e-12) -> None:
    if not math.isclose(float(a), float(b), rel_tol=rel, abs_tol=abs_tol):
        fail(f"{label} mismatch: {a!r} != {b!r}")


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def check_manifest() -> int:
    path = ROOT / "ARTIFACT_MANIFEST.sha256"
    listed: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, rel = line.split("  ", 1)
        rel = rel[2:] if rel.startswith("./") else rel
        if rel in listed:
            fail(f"duplicate manifest path: {rel}")
        listed[rel] = digest
    actual = {
        p.relative_to(ROOT).as_posix()
        for p in ROOT.rglob("*")
        if p.is_file() and p.name != path.name and not p.name.endswith(".tmp")
    }
    if set(listed) != actual:
        fail(f"manifest path set mismatch; unlisted={sorted(actual - set(listed))}; stale={sorted(set(listed) - actual)}")
    for rel, expected in listed.items():
        got = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        if got != expected:
            fail(f"manifest hash mismatch: {rel}")
    return len(listed)


def main() -> int:
    required = [
        "M1_ROWS.csv", "SUMMARY.csv", "GATE_REPORT.csv", "GATE_REPORT.md",
        "DEVIATIONS.md", "HANDOFF.md", "STATUS.md", "run_maf.py",
        "refit_vsoft.py", "results/verdict.json", "metrics/vsoft_channel_refit.csv",
        "spec/SPEC-M1-authored.md", "spec/SPEC-M1-R7-canonical-relay.txt",
    ]
    for rel in required:
        if not (ROOT / rel).is_file():
            fail(f"required file missing: {rel}")
    if "DEVIATION-041" not in (ROOT / "DEVIATIONS.md").read_text(encoding="utf-8"):
        fail("D-041 provenance mismatch is not recorded")
    r7 = (ROOT / "spec/SPEC-M1-R7-canonical-relay.txt").read_text(encoding="utf-8")
    for marker in ("R7-001", "R7-002", "R7-003", "V-SOVT", "V-SOFT"):
        if marker not in r7:
            fail(f"canonical R7 relay missing marker: {marker}")

    t2 = load_csv(ROOT / "M1_ROWS.csv")
    if len(t2) != 240:
        fail(f"T2 row count is {len(t2)}, expected 240")
    if list(t2[0]) != T2_COLUMNS:
        fail(f"T2 schema mismatch: {list(t2[0])}")
    counts = {(int(r["seed"]), r["variant_or_baseline"]): 0 for r in t2}
    for row in t2:
        seed = int(row["seed"])
        method = row["variant_or_baseline"]
        if seed not in SEEDS or method not in METHODS:
            fail(f"unexpected T2 key: {seed}, {method}")
        counts[(seed, method)] += 1
        finite(row["rmse_holdout"], f"T2 {seed}/{method} rmse_holdout")
        if method in LIVE_CHANNEL:
            finite(row["m_psi"], f"T2 {seed}/{method} m_psi")
            finite(row["m_dauroc"], f"T2 {seed}/{method} m_dauroc")
        elif row["m_psi"] != "" or row["m_dauroc"] != "":
            fail(f"non-channel columns populated for {seed}/{method}")
    if set(counts) != {(s, m) for s in SEEDS for m in METHODS} or any(v != 1 for v in counts.values()):
        fail("T2 does not contain exactly one row for every seed x method")

    metrics = {}
    metric_paths = sorted((ROOT / "metrics").glob("seed_*.json"))
    if len(metric_paths) != 240:
        fail(f"metric JSON count is {len(metric_paths)}, expected 240")
    for path in metric_paths:
        item = json.loads(path.read_text(encoding="utf-8"))
        key = (int(item["seed"]), item["method"])
        if key in metrics:
            fail(f"duplicate metric key: {key}")
        metrics[key] = item
        finite(item["rmse_holdout"], f"metric {key} rmse_holdout")
        for field in ("m_psi", "m_dauroc"):
            if item[field] is not None:
                finite(item[field], f"metric {key} {field}")
        row = next(r for r in t2 if (int(r["seed"]), r["variant_or_baseline"]) == key)
        close(item["rmse_holdout"], row["rmse_holdout"], f"metric/T2 {key} rmse_holdout")
        for field, col in (("m_psi", "m_psi"), ("m_dauroc", "m_dauroc")):
            if item[field] is None:
                # R7-002 permits the legacy V-SOFT JSON channel fields to
                # remain null when the deterministic refit table is emitted.
                if not (key[1] == "V-SOFT" and row[col] != ""):
                    if row[col] != "":
                        fail(f"metric/T2 blank mismatch for {key} {field}")
            else:
                close(item[field], row[col], f"metric/T2 {key} {field}")
    if set(metrics) != {(s, m) for s in SEEDS for m in METHODS}:
        fail("metric JSON key set mismatch")

    worlds = sorted((ROOT / "worlds").glob("seed_*.npz"))
    configs = sorted((ROOT / "configs").glob("seed_*.json"))
    if len(worlds) != 30 or len(configs) != 30:
        fail(f"world/config counts are {len(worlds)}/{len(configs)}, expected 30/30")
    config_data = {}
    for path in configs:
        item = json.loads(path.read_text(encoding="utf-8"))
        seed = int(item["seed"])
        config_data[seed] = item
        if item.get("b_scale") != 1.0:
            fail(f"unexpected b_scale for seed {seed}")
        if item.get("g0a_pass_scale") != 1.0 or item.get("g0b_lambda1_chosen") != 0.001:
            fail(f"gate constants mismatch for seed {seed}")
        if item.get("vsoft_channel_metrics_provenance") != "refit":
            fail(f"V-SOFT provenance missing/refuses refit for seed {seed}")
        if item.get("vsoft_channel_metrics_refit_runner") != "maf_v1/refit_vsoft.py":
            fail(f"V-SOFT refit runner mismatch for seed {seed}")
    if set(config_data) != set(SEEDS):
        fail("config seed set mismatch")
    if {p.stem for p in worlds} != {f"seed_{s}" for s in SEEDS}:
        fail("world seed set mismatch")

    refit = load_csv(ROOT / "metrics/vsoft_channel_refit.csv")
    if len(refit) != 30:
        fail(f"V-SOFT refit row count is {len(refit)}, expected 30")
    if list(refit[0]) != ["seed", "m_psi", "m_dauroc", "fit_seconds", "provenance"]:
        fail("V-SOFT refit schema mismatch")
    for row in refit:
        seed = int(row["seed"])
        if seed not in SEEDS or row["provenance"] != "refit":
            fail(f"invalid V-SOFT refit row: {row}")
        finite(row["m_psi"], f"refit {seed} m_psi")
        finite(row["m_dauroc"], f"refit {seed} m_dauroc")
        finite(row["fit_seconds"], f"refit {seed} fit_seconds")
        t2row = next(r for r in t2 if int(r["seed"]) == seed and r["variant_or_baseline"] == "V-SOFT")
        close(row["m_psi"], t2row["m_psi"], f"refit/T2 {seed} m_psi")
        close(row["m_dauroc"], t2row["m_dauroc"], f"refit/T2 {seed} m_dauroc")

    loss_paths = sorted((ROOT / "losses").glob("seed_*.json"))
    if len(loss_paths) != 120:
        fail(f"loss artifact count is {len(loss_paths)}, expected 120")
    for path in loss_paths:
        item = json.loads(path.read_text(encoding="utf-8"))
        method = path.stem.rsplit("_", 1)[1]
        if method == "V-ORAC":
            if item.get("epochs") is not None or item.get("steps") != 2000:
                fail(f"V-ORAC loss schedule mismatch in {path.name}")
        elif item.get("epochs") != 300 or item.get("steps") != 6000:
            fail(f"loss schedule mismatch in {path.name}")
        close(item.get("lambda1"), 0.001, f"loss lambda1 {path.name}")
        finite(item.get("fit_seconds"), f"loss fit_seconds {path.name}")

    gate_lines = {
        line.split(":", 1)[0].strip(): line.split(":", 1)[1].strip()
        for line in (ROOT / "GATE_REPORT.md").read_text(encoding="utf-8").splitlines()
        if ":" in line
    }
    if gate_lines.get("g0a_pass") != "True" or gate_lines.get("g0b_pass") != "True":
        fail("gate report does not show both gates passed")
    close(gate_lines["g0a_pass_scale"], 1.0, "gate g0a scale")
    close(gate_lines["g0b_lambda1_chosen"], 0.001, "gate lambda1")

    summary_rows = load_csv(ROOT / "SUMMARY.csv")
    if len(summary_rows) != 13 or [r["statistic"] for r in summary_rows] != SUMMARY_STATS:
        fail("summary is not the exact authored 13-row set")
    summary = {r["statistic"]: r["value"] for r in summary_rows}
    by_method = {m: {int(r["seed"]): r for r in t2 if r["variant_or_baseline"] == m} for m in METHODS}
    med = lambda method, col: statistics.median([finite(by_method[method][s][col], f"summary input {method}/{s}/{col}") for s in SEEDS])
    vfull = med("V-FULL", "rmse_holdout")
    baseline_meds = {b: med(b, "rmse_holdout") for b in BASELINES}
    best_name = min(baseline_meds, key=baseline_meds.get)
    best_rmse = baseline_meds[best_name]
    p1_rel = (best_rmse - vfull) / best_rmse
    p2 = med("V-FULL", "m_psi")
    p3 = med("V-FULL", "m_dauroc")
    k1 = statistics.median([100.0 * (finite(metrics[(s, "V-A0")]["rmse_heavy"], "k1 a0") - finite(metrics[(s, "V-FULL")]["rmse_heavy"], "k1 full")) / abs(finite(metrics[(s, "V-FULL")]["rmse_heavy"], "k1 full")) for s in SEEDS])
    k2 = statistics.median([100.0 * (finite(metrics[(s, "V-SOFT")]["rmse_heavy"], "k2 soft") - finite(metrics[(s, "V-FULL")]["rmse_heavy"], "k2 full")) / abs(finite(metrics[(s, "V-FULL")]["rmse_heavy"], "k2 full")) for s in SEEDS])
    k4 = med("V-ORAC", "m_psi")
    expected_summary = {
        "g0a_pass_scale": 1.0,
        "g0b_lambda1_chosen": 0.001,
        "g0b_best_correlation": float(gate_lines["g0b_best_correlation"]),
        "p1_vfull_rmse_median": vfull,
        "p1_best_baseline_name": best_name,
        "p1_best_baseline_rmse_median": best_rmse,
        "p1_relative_reduction": p1_rel,
        "p2_mpsi_median": p2,
        "p3_mdauroc_median": p3,
        "k1_gap_percent": k1,
        "k2_gap_percent": k2,
        "k4_vorac_mpsi_median": k4,
    }
    for key, expected in expected_summary.items():
        if key == "p1_best_baseline_name":
            if summary[key] != expected:
                fail(f"summary {key} mismatch: {summary[key]} != {expected}")
        else:
            close(summary[key], expected, f"summary {key}", rel=1e-10, abs_tol=1e-12)
    if summary["verdict_label"] != "PASS":
        fail(f"transmitted verdict is not PASS: {summary['verdict_label']}")
    result = json.loads((ROOT / "results/verdict.json").read_text(encoding="utf-8"))
    if result.get("verdict_label") != "PASS" or result.get("n_worlds") != 30 or result.get("n_methods") != 8:
        fail("results/verdict.json mismatch")

    manifest_count = check_manifest()
    print("MAF_PRODUCTION_VERIFY=PASS")
    print("t2_rows=240")
    print("summary_rows=13")
    print("worlds=30 configs=30 metrics=240 losses=120")
    print("r7_vsoft_refit_rows=30")
    print(f"manifest_entries={manifest_count}")
    print("summary_arithmetic=verified")
    print("verdict=PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"MAF_PRODUCTION_VERIFY=FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
