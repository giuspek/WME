# Weighted Model Enumeration (WME)

WME is a SAT-based framework for **Weighted Model Enumeration** with two solver variants and a benchmark suite.

- **`wme_cb/`** — Chronological backtracking version.
- **`wme_ncb/`** — Non-chronological backtracking version.
- **`test/`** — Benchmarks and example instances.

> **Build note:** To compile each variant, **follow the instructions inside** the corresponding directory (`wme_cb/` and `wme_ncb/`). Each folder contains its own build steps and dependencies.

---

## Directory Layout

```
.
├── wme_cb/     # WME with chronological backtracking (CB)
├── wme_ncb/    # WME with non-chronological backtracking (NCB)
└── test/       # Benchmarks and example inputs
```

---

## Requirements

Both variants require:
- **GMP** (GNU Multiple Precision Arithmetic Library)

### Ubuntu quick install

```bash
sudo apt update
sudo apt install -y libgmp-dev
```

This installs the development headers and static/shared libraries needed for compilation. Once installed, proceed with the build steps provided in each variant’s README (`wme_cb/README.md`, `wme_ncb/README.md`).

---

## Quick Start

1. **Build a solver variant**
   - See `wme_cb/README.md` for CB build steps.
   - See `wme_ncb/README.md` for NCB build steps.

2. **Run on a benchmark**
   - After building, run the produced binary on files from `test/`. (Paths/flags may differ by variant.)
   ```bash
   ./wme_cb/build/wme_cb <path-to-test-instance>
   # or
   ./wme_ncb/build/wme_ncb <path-to-test-instance>
   ```

---

## Benchmarks

The `test/` folder includes benchmark instances for quick validation and performance checks. Refer to the per-variant README for any flags (e.g., weight files, enumeration limits, verbosity).

---

## Citing

If you use WME in academic work, please cite the project (add your preferred citation here).


---

## Contact

For questions or issues, please open a GitHub issue or contact the maintainer at gs81 <at> rice <dot> edu.
