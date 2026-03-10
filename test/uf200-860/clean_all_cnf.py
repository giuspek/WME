#!/usr/bin/env python3
# clean_all_cnf.py — minimal in-place DIMACS CNF cleaner for all *.cnf in this folder.
# Put this file in the directory with your CNFs and run:  `python3 clean_all_cnf.py`

from pathlib import Path
import tempfile

def parse_cnf(text: str):
    clauses, cur = [], []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith('c') or line.startswith('%') or line.startswith('p '):
            continue
        for tok in line.split():
            try:
                lit = int(tok)
            except ValueError:
                continue  # ignore junk
            if lit == 0:
                if cur:
                    clauses.append(cur)
                    cur = []
            else:
                cur.append(lit)
    # drop any unterminated trailing clause (safer than guessing)
    nvars = max((abs(l) for cl in clauses for l in cl), default=0)
    return nvars, clauses

def write_cnf(path: Path, nvars: int, clauses):
    lines = ["c cleaned in-place by clean_all_cnf.py",
             f"p cnf {nvars} {len(clauses)}"]
    for cl in clauses:
        lines.append(" ".join(map(str, (l for l in cl if l != 0))) + " 0")
    tmp = Path(tempfile.mkstemp(prefix=path.name, dir=str(path.parent))[1])
    tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    tmp.replace(path)  # atomic-ish overwrite

def main():
    here = Path(".")
    files = sorted(here.glob("*.cnf"))
    if not files:
        print("No *.cnf files found here.")
        return
    for cnf in files:
        txt = cnf.read_text(encoding="utf-8", errors="ignore")
        nvars, clauses = parse_cnf(txt)
        write_cnf(cnf, nvars, clauses)
        print(f"[OK] {cnf.name}  (vars={nvars}, clauses={len(clauses)})")

if __name__ == "__main__":
    main()
