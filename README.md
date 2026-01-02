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
   ./wme_cb/build/wme_cb <file.cnf> --weights <file.weights>
   # or
   ./wme_ncb/build/wme_ncb <file.cnf> --weights <file.weights>
   ```

   Running the tool without a .weights file assumes all variables have 1 as weight, both positive and negative.

   **Other options**

    ```bash
   --topk <n>: enumerate the best topk models
   --threshold <r>: enumerate all solutions whose weight is higher than the threshold
   --logthreshold <r>: enumerate all solution whose weight is higher than the log10 of the threshold
   ```

   Notice that topk can be combined with the other two options, but threshold and logthreshold cannot be assigned for the same instance.


---

## Benchmarks

The `test/` folder includes benchmark instances for quick validation and performance checks. In particular:

```
.
├── bayes-basic/    # Benchmark on bayesian network WMC encoding with high number of variables and complex structure
├── bayes-or/    # Benchmark on bayesian network WMC encoding with low number of variables and easier structure
└── rnd3sat-weights/       # Benchmarks on synthetic random 3SAT problems
```

---

## Citing

If you use WME in academic work, please cite the project:


---

## Contact

For questions or issues, please open a GitHub issue or contact the maintainer at gs81 [at] rice [dot] edu.
