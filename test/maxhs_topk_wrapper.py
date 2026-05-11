#!/usr/bin/env python3

import argparse
import subprocess
import tempfile
import os
import re
import time


def parse_wcnf(path):
    comments = []
    clauses = []
    nvars = 0
    top = None

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("c"):
                comments.append(line)
            elif line.startswith("p"):
                parts = line.split()
                nvars = int(parts[2])
                top = int(parts[4])
            else:
                parts = list(map(int, line.split()))
                weight = parts[0]
                lits = parts[1:-1]
                clauses.append((weight, lits))

    return comments, nvars, top, clauses


def write_wcnf(path, comments, nvars, top, clauses):
    with open(path, "w") as f:
        for c in comments:
            f.write(c + "\n")
        f.write(f"p wcnf {nvars} {len(clauses)} {top}\n")
        for w, lits in clauses:
            f.write(f"{w} {' '.join(map(str, lits))} 0\n")


def run_maxhs(bin_path, instance, remaining_time):
    try:
        result = subprocess.run(
            [bin_path, instance, "-printSoln"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=max(1, int(remaining_time))
        )
        return result.stdout + "\n" + result.stderr, False
    except subprocess.TimeoutExpired as e:
        out = ""
        if e.stdout:
            out += e.stdout
        if e.stderr:
            out += "\n" + e.stderr
        out += "\nc DEBUG: subprocess timeout expired\n"
        return out, True


def parse_model(output):
    cost = None
    bitstring = None
    cpu_time = None

    for raw in output.splitlines():
        line = raw.strip()
        if not line:
            continue

        if line.startswith("o "):
            parts = line.split()
            if len(parts) >= 2:
                try:
                    cost = int(parts[1])
                except ValueError:
                    pass

        if line.startswith("v"):
            payload = line[1:].strip()
            payload = re.sub(r"\s+", "", payload)
            if payload and all(ch in "01" for ch in payload):
                bitstring = payload

        m = re.match(r"^c\s+CPU:\s*([0-9]+(?:\.[0-9]+)?)$", line)
        if m:
            cpu_time = m.group(1)

    return bitstring, cost, cpu_time


def blocking_clause_from_bitstring(bitstring):
    clause = []
    for i, bit in enumerate(bitstring, start=1):
        clause.append(-i if bit == "1" else i)
    return clause


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bin", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--k", type=int, default=50)
    parser.add_argument("--timeout", type=int, default=600,
                        help="Total timeout in seconds for the whole top-k run")
    args = parser.parse_args()

    comments, nvars, top, clauses = parse_wcnf(args.input)

    found = 0
    blocking_hards = []
    last_cpu = "-1"

    start_time = time.time()
    timed_out = False

    with tempfile.TemporaryDirectory() as tmp:
        inst = os.path.join(tmp, "inst.wcnf")

        while found < args.k:
            elapsed = time.time() - start_time
            remaining = args.timeout - elapsed

            if remaining <= 0:
                print("c DEBUG: total timeout reached before next iteration")
                timed_out = True
                break

            all_clauses = list(clauses) + [(top, c) for c in blocking_hards]
            write_wcnf(inst, comments, nvars, top, all_clauses)

            out, sub_timeout = run_maxhs(args.bin, inst, remaining)
            bitstring, cost, cpu_time = parse_model(out)

            if cpu_time is not None:
                last_cpu = cpu_time

            if sub_timeout:
                print(out)
                timed_out = True
                break

            if bitstring is None:
                print("c DEBUG: raw solver output follows")
                print(out)
                print("c DEBUG: no bitstring model found in solver output")
                break

            found += 1
            print(f"c TOPK {found} cost={cost}")
            print(f"c TOPK-MODEL {bitstring}")

            block = blocking_clause_from_bitstring(bitstring)
            print("c BLOCK " + " ".join(map(str, block)))
            blocking_hards.append(block)

        total_elapsed = time.time() - start_time
        print(f"c TOPK-FOUND {found}")
        print(f"c FINAL-CPU {last_cpu}")
        print(f"c TOTAL-WALL {total_elapsed:.4f}")
        print(f"c TIMEOUT {1 if timed_out else 0}")


if __name__ == "__main__":
    main()