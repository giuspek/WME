#!/usr/bin/env python3

import argparse
import math
from pathlib import Path


def parse_wcnf(path):
    nvars = None
    top = None

    hard_clauses = []
    soft_units = []

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()

            if not line or line.startswith("c"):
                continue

            if line.startswith("p "):
                parts = line.split()
                if len(parts) < 5 or parts[1] != "wcnf":
                    raise ValueError(
                        f"{path}:{lineno}: expected header 'p wcnf nvars nclauses top'"
                    )

                nvars = int(parts[2])
                top = int(parts[4])
                continue

            if nvars is None or top is None:
                raise ValueError(f"{path}:{lineno}: clause before WCNF header")

            nums = [int(x) for x in line.split()]
            if not nums or nums[-1] != 0:
                raise ValueError(f"{path}:{lineno}: clause does not end with 0")

            weight = nums[0]
            clause = nums[1:-1]

            if weight >= top:
                hard_clauses.append(clause)
            else:
                if len(clause) != 1:
                    raise ValueError(
                        f"{path}:{lineno}: non-unit soft clause {clause}. "
                        "This converter only supports unit soft clauses."
                    )
                soft_units.append((weight, clause[0]))

    if nvars is None:
        raise ValueError(f"{path}: missing WCNF header")

    return nvars, hard_clauses, soft_units


def convert_file(input_path, output_dir):
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    nvars, hard_clauses, soft_units = parse_wcnf(input_path)

    if soft_units:
        max_soft = max(cost for cost, _ in soft_units)
    else:
        max_soft = 1

    weights = {lit: 1.0 for v in range(1, nvars + 1) for lit in (v, -v)}

    for cost, lit in soft_units:
        if cost <= 0:
            raise ValueError(f"{input_path}: soft cost must be positive, found {cost}")

        falsifying_lit = -lit
        penalty = math.exp(-cost / max_soft)

        # In case several soft unit clauses penalize the same literal,
        # multiply the penalties. This corresponds to adding MaxSAT costs.
        weights[falsifying_lit] *= penalty

    stem = input_path.stem

    cnf_path = output_dir / f"{stem}.cnf"
    weights_path = output_dir / f"{stem}.weights"

    with open(cnf_path, "w", encoding="utf-8") as f:
        f.write(f"c converted from {input_path.name}\n")
        f.write("c hard clauses only\n")
        f.write(f"p cnf {nvars} {len(hard_clauses)}\n")

        for clause in hard_clauses:
            f.write(" ".join(map(str, clause)) + " 0\n")

    with open(weights_path, "w", encoding="utf-8") as f:
        f.write(f"c weights converted from {input_path.name}\n")
        f.write("c unit-soft MaxSAT to WME conversion\n")
        f.write("c soft clause (cost lit 0) gives weight exp(-cost/max_soft) to -lit\n")
        f.write(f"c max_soft {max_soft}\n")
        f.write("c objective equivalence: maximizing product of weights equals minimizing MaxSAT cost\n")

        for v in range(1, nvars + 1):
            f.write(f"{v} {weights[v]:.17g}\n")
            f.write(f"{-v} {weights[-v]:.17g}\n")

    return cnf_path, weights_path, len(hard_clauses), len(soft_units), max_soft


def collect_wcnf_files(input_path):
    input_path = Path(input_path)

    if input_path.is_file():
        return [input_path]

    files = []
    for pattern in ("*.wcnf", "*.maxsat", "*.txt"):
        files.extend(input_path.rglob(pattern))

    return sorted(set(files))


def main():
    parser = argparse.ArgumentParser(
        description="Convert unit-soft WCNF MaxSAT instances to WME CNF + weights."
    )

    parser.add_argument(
        "input",
        help="Input WCNF file or directory containing WCNF files.",
    )

    parser.add_argument(
        "-o",
        "--output",
        default="WME",
        help="Output directory. Default: WME",
    )

    args = parser.parse_args()

    files = collect_wcnf_files(args.input)

    if not files:
        print(f"No WCNF files found in {args.input}")
        return

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = output_dir / "manifest.csv"

    converted = 0
    skipped = 0

    with open(manifest_path, "w", encoding="utf-8") as mf:
        mf.write("input,cnf,weights,n_hard,n_soft,max_soft\n")

        for path in files:
            try:
                cnf_path, weights_path, n_hard, n_soft, max_soft = convert_file(
                    path,
                    output_dir,
                )

                mf.write(
                    f"{path},{cnf_path},{weights_path},{n_hard},{n_soft},{max_soft}\n"
                )

                print(f"[OK] {path} -> {cnf_path.name}, {weights_path.name}")
                converted += 1

            except Exception as e:
                print(f"[SKIP] {path}: {e}")
                skipped += 1

    print()
    print(f"Converted: {converted}")
    print(f"Skipped:   {skipped}")
    print(f"Manifest:  {manifest_path}")


if __name__ == "__main__":
    main()