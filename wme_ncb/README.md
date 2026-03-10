[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# WME_NCB — Weighted Model Enumeration with Non-Chronological Backtracking

This repository contains **WME_NCB**, a **Weighted Model Enumeration (WME)** solver built on top of a lightly modified **CaDiCaL** backend.

The solver is designed for **enumeration under literal weights**, with support for:

- **full weighted enumeration**,
- **threshold-based filtering**, and
- **top-\(k\)** search.

The backend is CaDiCaL, but this repository should be used as a **WME tool first**. Most CaDiCaL options are not important for typical WME usage; the key options are the WME-specific ones documented below.

> If you are looking for the original CaDiCaL SAT solver, see the upstream repository by Armin Biere.

## Build

Use the standard build procedure:

```bash
./configure && make
```

The main executable is:

```bash
build/wme_ncb
```

## Basic usage

The solver expects a **DIMACS CNF** instance and can optionally take a **weights file**.

```bash
build/wme_ncb [WME options] input.cnf
```

Typical usage patterns are:

### 1. Enumerate all models

```bash
build/wme_ncb input.cnf
```

If no weights file is provided, all literal weights default to `1`, so the solver behaves like an unweighted enumerator.

### 2. Enumerate weighted models

```bash
build/wme_ncb --weights weights.txt input.cnf
```

### 3. Return only the top-\(k\) models

```bash
build/wme_ncb --weights weights.txt --topk 10 input.cnf
```

### 4. Enumerate only models above a threshold

```bash
build/wme_ncb --weights weights.txt --logthreshold -3 input.cnf
```

or equivalently, if you prefer specifying the threshold in the original scale:

```bash
build/wme_ncb --weights weights.txt --threshold 0.001 input.cnf
```

## WME-specific options

These are the main options relevant for weighted enumeration.

### `--weights <file>`

Loads literal weights from `<file>`.

```bash
build/wme_ncb --weights weights.txt input.cnf
```

If omitted, the solver assigns weight `1` to both polarities of every variable.

### `--topk <k>`

Keeps only the **top-\(k\)** models according to the weighted objective.

```bash
build/wme_ncb --weights weights.txt --topk 5 input.cnf
```

Important notes:

- `k` must be a **positive integer**.
- In top-\(k\) mode, the solver stores the current best `k` solutions and prints them at the end.
- Internally, the current worst solution among the top `k` becomes the active pruning bound.

### `--threshold <value>`

Sets a threshold in the **original numeric scale**.

```bash
build/wme_ncb --weights weights.txt --threshold 0.01 input.cnf
```

This is convenient when weights are interpreted multiplicatively and the user wants to reason directly in the original scale.

### `--logthreshold <value>`

Sets the threshold directly in **log10 scale**.

```bash
build/wme_ncb --weights weights.txt --logthreshold -2 input.cnf
```

This avoids manual conversion when your weights are already handled in logarithmic form.

### `--witness` / `--no-witness`

Controls witness printing in the underlying solver interface. For WME runs, the relevant output is the enumeration output described below.

## Weights file format

The weights file is a plain text file with **one literal per line**:

```text
<literal> <weight>
```

Example:

```text
1 0.8
-1 0.2
2 0.3
-2 0.7
3 1.0
-3 1.0
```

Meaning:

- literal `1` has weight `0.8`
- literal `-1` has weight `0.2`
- literal `2` has weight `0.3`
- literal `-2` has weight `0.7`

Remarks:

- Both positive and negative literals can be assigned explicitly.
- Lines starting with `c` are treated as comments.
- Weights are parsed as arbitrary-precision numeric values through GMP, so decimal and rational-style inputs are accepted by the parser.

## Which variables matter for ranking?

The solver automatically identifies **weight-relevant variables**.

A variable is considered relevant only when its two polarities have **different weights**. If

```text
w(x) = w(¬x)
```

then that variable does not affect model ranking and is treated as weight-irrelevant for pruning and top-\(k\) comparisons.

This is important in practice because Tseitin or encoding-introduced variables often have equal weights on both polarities and therefore should not influence the ranking logic.

## Output format

### Full enumeration mode

When `--topk` is **not** used, the solver prints each discovered model as it is found.

Each output line contains:

- the literals in the current satisfying assignment,
- the exact multiplicative weight in parentheses,
- the accumulated log-score in square brackets.

The final line is:

```text
s <num_models>
```

where `<num_models>` is the number of models enumerated.

### Top-\(k\) mode

When `--topk k` is enabled, intermediate models are not printed in final ranked form immediately. At the end, the solver prints the retained top-\(k\) assignments, each prefixed by:

```text
t
```

followed by the assignment and its score, and finally the summary line:

```text
s <num_models>
```

Here `num_models` is the number of satisfying assignments found during search, while the printed `t` lines are the best retained solutions.

## Recommended workflows

### Enumerate everything

```bash
build/wme_ncb --weights weights.txt input.cnf
```

Use this when you want all satisfying assignments together with their weights.

### Keep only the best solutions

```bash
build/wme_ncb --weights weights.txt --topk 20 input.cnf
```

Use this when the search space is large and you only need the highest-scoring assignments.

### Prune below a fixed quality bar

```bash
build/wme_ncb --weights weights.txt --threshold 1e-4 input.cnf
```

Use this when you want to enumerate only solutions whose score is above a given bound.

## Practical notes

- The input formula must be in **CNF (DIMACS)**.
- If no weights file is given, the solver falls back to **unit weights**.
- `--threshold` and `--logthreshold` are **mutually exclusive**.
- `--topk` requires a positive integer.
- For WME experiments, the most important options are usually just:
  - `--weights`
  - `--topk`
  - `--threshold` or `--logthreshold`

## Citation

If you use this code in academic work, please cite the accompanying WME paper.
