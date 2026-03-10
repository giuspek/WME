# Weighted Model Enumeration (WME)

WME is a SAT-based framework for **Weighted Model Enumeration** with two solver variants and a benchmark suite.

- **`wme_cb/`** — Chronological backtracking version.
- **`wme_ncb/`** — Non-chronological backtracking version.
- **`test/`** — Benchmarks and example instances.

> **Build note:** To compile each variant, **follow the instructions inside** the corresponding directory (`wme_cb/` and `wme_ncb/`). Each folder contains its own build steps and dependencies.

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

---

## Benchmarks

The `test/` folder includes benchmark instances for quick validation and performance checks. In particular:

```
.
├── bayes-basic/    # Benchmark on bayesian network WMC encoding with high number of variables and complex structure
├── bayes-or/    # Benchmark on bayesian network WMC encoding with low number of variables and easier structure
├── uf200-860/     # Benchmark on SATLIB problems with ratio clauses-to-variables 4.28
└── rnd3sat-1.5/       # Benchmarks on synthetic random 3SAT problems with ratio clauses-to-variables 1.5
```

---

## Citing

If you use WME in academic work, please cite the project:


---

## Contact

For questions or issues, please open a GitHub issue or contact the maintainer at gs81 [at] rice [dot] edu.
