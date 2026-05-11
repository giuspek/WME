# Weighted Model Enumeration (WME)

WME is a SAT-based framework for **Weighted Model Enumeration** with two solver variants and a benchmark suite.

- **`wme_cb/`** - Chronological backtracking version.
- **`wme_ncb/`** - Non-chronological backtracking version.
- **`test/`** - Benchmarks, regression tests, and example instances.

> **Build note:** WME can now be built from the repository root. The top-level `makefile` configures and builds both solver variants.

---

## Requirements

Both variants require:
- **GMP** (GNU Multiple Precision Arithmetic Library)

### Ubuntu quick install

```bash
sudo apt update
sudo apt install -y libgmp-dev
```

This installs the development headers and static/shared libraries needed for compilation.

---

## Quick Start

Build both solver variants from the repository root:

```bash
make
```

Build only one variant:

```bash
make cb
make ncb
```

Run the integration tests:

```bash
make test
```

Clean generated build files:

```bash
make clean
```

---

## Benchmarks

The `test/` folder includes benchmark instances for quick validation and performance checks. In particular:

```text
.
|-- bayes-basic/    # Bayesian-network WMC encodings with many variables
|-- bayes-or/       # Easier Bayesian-network WMC encodings
|-- uf200-860/      # SATLIB problems with clause/variable ratio 4.28
`-- rnd3sat-1.5/    # Synthetic random 3SAT benchmarks
```

---

## Citing

If you use WME in academic work, please cite the project:


---

## Contact

For questions or issues, please open a GitHub issue or contact the maintainer at gs81 [at] rice [dot] edu.
