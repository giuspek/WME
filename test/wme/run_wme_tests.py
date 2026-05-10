#!/usr/bin/env python3

import argparse
import math
import re
import subprocess
import sys
from decimal import Decimal
from pathlib import Path


WME_ROOT = Path(__file__).resolve().parents[2]
CASES = WME_ROOT / "test" / "wme" / "cases"
BENCHMARKS = WME_ROOT / "test"
MODEL_PREFIX = re.compile(r"^(?:t\s+|[|*\s-]*\d)")
INT_RE = re.compile(r"-?\d+")
WEIGHT_REL_TOL = Decimal("1e-12")
WEIGHT_ABS_TOL = Decimal("1e-300")


class Model:
    def __init__(self, assignment, weight):
        self.assignment = assignment
        self.weight = weight


class Mode:
    def __init__(self, name, binary, prefix):
        self.name = name
        self.binary = binary
        self.prefix = prefix

    def command(self, args):
        return [str(self.binary)] + self.prefix + args


def normalize_assignment(lits):
    return tuple(sorted(lits, key=lambda lit: abs(lit)))


def parse_models(output):
    models = []
    for raw in output.splitlines():
        line = raw.strip()
        if not line or line.startswith(("c ", "s ", "v ")):
            continue
        if "(" not in line or ")" not in line:
            continue
        before_weight, after_weight = line.split("(", 1)
        if not MODEL_PREFIX.match(before_weight.strip()):
            continue
        if before_weight.lstrip().startswith("t "):
            before_weight = before_weight.lstrip()[2:]
        lits = [int(token) for token in INT_RE.findall(before_weight.replace("|", " ").replace("*", " "))]
        if not lits:
            continue
        weight_text = after_weight.split(")", 1)[0].strip()
        models.append(Model(normalize_assignment(lits), Decimal(weight_text)))
    return models


def run_solver(mode, args):
    cmd = mode.command(args)
    completed = subprocess.run(
        cmd,
        cwd=WME_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )
    if completed.returncode not in (0, 10, 20):
        raise AssertionError(
            f"command failed with exit code {completed.returncode}: {' '.join(cmd)}\n"
            f"{completed.stdout}"
        )
    models = parse_models(completed.stdout)
    if not models:
        raise AssertionError(
            f"command produced no parseable models: {' '.join(cmd)}\n"
            f"{completed.stdout}"
        )
    return models


def expect_failure(mode, args, label):
    cmd = mode.command(args)
    completed = subprocess.run(
        cmd,
        cwd=WME_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )
    if completed.returncode in (0, 10, 20):
        raise AssertionError(
            f"{label}: expected command to fail, got exit code {completed.returncode}: "
            f"{' '.join(cmd)}\n{completed.stdout}")


def model_map(models, label):
    result = {}
    for model in models:
        if model.assignment in result:
            raise AssertionError(f"{label}: duplicate model {model.assignment}")
        result[model.assignment] = model.weight
    return result


def sorted_by_weight(models):
    return sorted(models, key=lambda model: (model.weight, model.assignment), reverse=True)


def assert_same_models(left, right, label):
    left_map = model_map(left, label + " left")
    right_map = model_map(right, label + " right")
    if left_map != right_map:
        raise AssertionError(
            f"{label}: model sets differ\n"
            f"left={sorted(left_map.items())}\n"
            f"right={sorted(right_map.items())}")


def assert_same_weight_profile(left, right, label):
    left_weights = sorted([model.weight for model in left], reverse=True)
    right_weights = sorted([model.weight for model in right], reverse=True)
    if len(left_weights) != len(right_weights):
        raise AssertionError(
            f"{label}: top-k weight profile lengths differ\n"
            f"left={left_weights}\n"
            f"right={right_weights}")
    for idx, (left_weight, right_weight) in enumerate(zip(left_weights, right_weights), 1):
        if weights_close(left_weight, right_weight):
            continue
        raise AssertionError(
            f"{label}: top-k weight profiles differ at rank {idx}\n"
            f"left={left_weights}\n"
            f"right={right_weights}")


def weights_close(left, right):
    if left == right:
        return True
    diff = abs(left - right)
    scale = max(abs(left), abs(right))
    if scale == 0:
        return diff <= WEIGHT_ABS_TOL
    return diff <= max(WEIGHT_ABS_TOL, scale * WEIGHT_REL_TOL)


def assert_model_count(models, expected, label):
    if len(models) != expected:
        raise AssertionError(f"{label}: expected {expected} models, got {len(models)}")


def assert_topk_matches_full(full, topk, k, label):
    full_map = model_map(full, label + " full")
    topk_map = model_map(topk, label + " topk")
    expected_count = min(k, len(full))
    if len(topk) != expected_count:
        raise AssertionError(f"{label}: expected {expected_count} top-k models, got {len(topk)}")
    missing_from_full = set(topk_map) - set(full_map)
    if missing_from_full:
        raise AssertionError(f"{label}: top-k returned models absent from full enum: {missing_from_full}")

    ranked_full = sorted_by_weight(full)
    kth_weight = ranked_full[expected_count - 1].weight
    for assignment, weight in topk_map.items():
        if weight < kth_weight:
            raise AssertionError(
                f"{label}: top-k model {assignment} has weight {weight}, below kth full weight {kth_weight}"
            )

    required = {model.assignment for model in ranked_full if model.weight > kth_weight}
    missing_required = required - set(topk_map)
    if missing_required:
        raise AssertionError(f"{label}: top-k missed strictly better models: {missing_required}")


def assert_threshold_matches_full(full, thresholded, threshold, label):
    threshold = Decimal(threshold)
    expected = [model for model in full if model.weight >= threshold]
    assert_same_models(expected, thresholded, label)


def weights_args(name):
    return ["--weights", str(CASES / f"{name}.weights"), str(CASES / f"{name}.cnf")]


def benchmark_weights_args(directory, stem):
    root = BENCHMARKS / directory
    return ["--weights", str(root / f"{stem}.weights"), str(root / f"{stem}.cnf")]


def benchmark_cnf_args(directory, filename):
    return [str(BENCHMARKS / directory / filename)]


def wcnf_args(name):
    return ["--wcnf", str(CASES / f"{name}.wcnf")]


def supports_option(mode, option):
    completed = subprocess.run(
        mode.command(["--help"]),
        cwd=WME_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )
    return option in completed.stdout


def test_topk_against_full(modes, name, k):
    topk_by_mode = {}
    for mode in modes:
        full = run_solver(mode, weights_args(name))
        topk = run_solver(mode, ["--topk", str(k)] + weights_args(name))
        assert_topk_matches_full(full, topk, k, f"{name} {mode.name}")
        topk_by_mode[mode.name] = topk
    assert_same_models(topk_by_mode["NCB"], topk_by_mode["CB"], f"{name} CB vs NCB top-k")


def test_wcnf_equivalence(modes, name, k):
    for mode in modes:
        split = run_solver(mode, ["--topk", str(k)] + weights_args(name))
        embedded = run_solver(mode, ["--topk", str(k)] + wcnf_args(name))
        assert_same_models(split, embedded, f"{name} {mode.name} --weights vs --wcnf")


def test_threshold_equivalence(mode, name, threshold):
    log_threshold = f"{math.log10(float(threshold)):.17g}"
    full = run_solver(mode, weights_args(name))
    linear = run_solver(mode, ["--threshold", threshold] + weights_args(name))
    logged = run_solver(mode, ["--logthreshold", log_threshold] + weights_args(name))
    assert_threshold_matches_full(full, linear, threshold, f"{name} {mode.name} threshold vs full enum")
    assert_same_models(linear, logged, f"{name} {mode.name} threshold vs logthreshold")


def test_invalid_inputs(modes, have_wcnf):
    for mode in modes:
        expect_failure(
            mode,
            ["--weights", str(CASES / "invalid_zero.weights"),
             str(CASES / "topk_basic.cnf")],
            f"{mode.name}: zero weight is rejected")
        expect_failure(
            mode,
            ["--weights", str(CASES / "invalid_negative.weights"),
             str(CASES / "topk_basic.cnf")],
            f"{mode.name}: negative weight is rejected")
        if have_wcnf:
            expect_failure(
                mode,
                ["--weights", str(CASES / "topk_basic.weights"),
                 "--wcnf", str(CASES / "topk_basic.cnf")],
                f"{mode.name}: --weights and --wcnf are mutually exclusive")


def test_benchmark_cb_ncb_topk(modes, label, args, k):
    ncb = run_solver(modes[0], ["--topk", str(k)] + args)
    cb = run_solver(modes[1], ["--topk", str(k)] + args)
    assert_model_count(ncb, k, label + " NCB")
    assert_model_count(cb, k, label + " CB")
    assert_same_weight_profile(ncb, cb, label + " CB vs NCB")


def build_modes(paths):
    if len(paths) == 1:
        binary = Path(paths[0])
        if not binary.is_absolute():
            binary = (Path.cwd() / binary).resolve()
        return [Mode("NCB", binary, ["--ncb"]), Mode("CB", binary, ["--cb"])]
    if len(paths) == 2:
        cb = Path(paths[0])
        ncb = Path(paths[1])
        if not cb.is_absolute():
            cb = (Path.cwd() / cb).resolve()
        if not ncb.is_absolute():
            ncb = (Path.cwd() / ncb).resolve()
        return [Mode("NCB", ncb, []), Mode("CB", cb, [])]
    raise AssertionError("expected either one wrapper binary or CB and NCB binaries")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("binaries", nargs="+", help="one wrapper binary or CB and NCB binaries")
    args = parser.parse_args()

    modes = build_modes(args.binaries)
    for mode in modes:
        if not mode.binary.exists():
            print(f"missing WME binary: {mode.binary}", file=sys.stderr)
            return 1
    ncb_mode = next(mode for mode in modes if mode.name == "NCB")
    cb_mode = next(mode for mode in modes if mode.name == "CB")

    have_wcnf = all(supports_option(mode, "--wcnf") for mode in modes)

    tests = [
        ("topk_basic: full enum vs top-k, CB/NCB",
         lambda: test_topk_against_full(modes, "topk_basic", 5)),
        ("unit_before_weights: full enum vs top-k, CB/NCB",
         lambda: test_topk_against_full(modes, "unit_before_weights", 2)),
        ("relevant_irrelevant: full enum vs top-k, CB/NCB",
         lambda: test_topk_against_full(modes, "relevant_irrelevant", 4)),
        ("topk_basic NCB: --threshold vs --logthreshold",
         lambda: test_threshold_equivalence(ncb_mode, "topk_basic", "0.1")),
        ("topk_basic CB: --threshold vs --logthreshold",
         lambda: test_threshold_equivalence(cb_mode, "topk_basic", "0.1")),
        ("relevant_irrelevant NCB: --threshold vs --logthreshold",
         lambda: test_threshold_equivalence(ncb_mode, "relevant_irrelevant", "0.08")),
        ("relevant_irrelevant CB: --threshold vs --logthreshold",
         lambda: test_threshold_equivalence(cb_mode, "relevant_irrelevant", "0.08")),
        ("invalid inputs are rejected",
         lambda: test_invalid_inputs(modes, have_wcnf)),
        ("benchmark bayes-basic/50-10-1-q: CB vs NCB top-k",
         lambda: test_benchmark_cb_ncb_topk(
             modes, "bayes-basic/50-10-1-q",
             benchmark_weights_args("bayes-basic", "50-10-1-q"), 5)),
        ("benchmark maxsat-comp/8.wcsp.dir: CB vs NCB top-k",
         lambda: test_benchmark_cb_ncb_topk(
             modes, "maxsat-comp/8.wcsp.dir",
             benchmark_weights_args("maxsat-comp", "8.wcsp.dir"), 5)),
        ("benchmark mc/mc2020_track2_000: CB vs NCB top-k",
         lambda: test_benchmark_cb_ncb_topk(
             modes, "mc/mc2020_track2_000",
             benchmark_weights_args("mc", "mc2020_track2_000"), 5)),
        ("benchmark rnd3sat-1.5/rnd3sat-w-25-0: CB vs NCB top-k",
         lambda: test_benchmark_cb_ncb_topk(
             modes, "rnd3sat-1.5/rnd3sat-w-25-0",
             benchmark_cnf_args("rnd3sat-1.5", "rnd3sat-w-25-0.cnf"), 5)),
        ("benchmark uf200-860/uf200-01: CB vs NCB top-k",
         lambda: test_benchmark_cb_ncb_topk(
             modes, "uf200-860/uf200-01",
             benchmark_weights_args("uf200-860", "uf200-01"), 5)),
    ]
    if have_wcnf:
        tests.insert(3, ("topk_basic: --weights vs --wcnf",
                         lambda: test_wcnf_equivalence(modes, "topk_basic", 5)))

    failures = []
    for name, test in tests:
        sys.stdout.write(f"wme test: {name} ... ")
        sys.stdout.flush()
        try:
            test()
        except Exception as err:
            print("FAIL")
            failures.append((name, err))
        else:
            print("ok")

    if failures:
        print("")
        print(f"{len(failures)} of {len(tests)} WME integration checks failed:")
        for index, (name, err) in enumerate(failures, 1):
            print("")
            print(f"{index}) {name}")
            print(str(err))
        return 1

    print(f"wme integration tests passed ({len(tests)} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
