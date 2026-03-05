[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

WME_CB — Weighted Model Enumeration (with Chronological Backtracking)
===============================================================================

This repository implements **WME_CB**, a **Weighted Model Enumeration (WME)** engine based on **CDCL with chronological backtracking**.  
The focus is on enumeration-oriented solver control and weight-aware handling needed to generate (or rank/filter) satisfying assignments under weights.

This codebase uses a lightly modified **CaDiCaL** SAT solver as its backend. CaDiCaL provides the underlying CDCL core; WME_CB builds the weighted-enumeration logic on top of it.

## What you get

- **Weighted model enumeration** workflows (WME_CB)
- A **CaDiCaL-based backend** (included in this repository) used to execute the CDCL search and expose the hooks needed for WME

> If you are only looking for CaDiCaL itself (upstream SAT solver), see:
> https://github.com/arminbiere/cadical

## Build

Use the standard CaDiCaL-style build procedure:

```bash
./configure && make
