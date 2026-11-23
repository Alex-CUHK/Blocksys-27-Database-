# Workload Informed EVM Architecture and Floorplanning

**Initiator:** [Alex-CUHK](https://github.com/Alex-CUHK)  
**Email:** alexus20568@gmail.com

This repository contains the original SQD block data, static eight-module experiment, workload-informed proxy matrices, exact placement searches, audits, scripts, and manuscript artifacts for Ethereum Mainnet, OP Mainnet, and Arbitrum One.

## Start here

- [Eight-module matrix and experiment workflow](experiment/EIGHT_MODULE_MATRIX_WORKFLOW.txt)
- [Current experiment methodology](experiment/outputs/workload_weighted/methodology.md)
- [Results and interpretation](experiment/outputs/workload_weighted/paper_sections.md)
- [Latest manuscript PDF](manuscript/samplepaper.pdf)
- [Overleaf project](https://www.overleaf.com/project/6af9611166228c8dee747d69)

## Materials

| Location | Contents |
|---|---|
| `data/raw/` | 228 original compressed block files and the original sampling calendar |
| `data/manifest.json` | Current raw-file sizes and SHA256 hashes |
| `data/original_source_manifest.json` | Original delivery manifest, including the historical Chinese source-note paths |
| `data/docs/` | English sampling design and field dictionary, with inherited-plan discrepancies identified |
| `experiment/` | Static model, original nine-block pilot, RPC probes, tests, current weighted model, and English workflow |
| `experiment/outputs/workload_weighted/` | 216 hourly matrices, split and normalization, 4,320 scenario rows, trained layouts, controls, sensitivity results, audits and figures |
| `manuscript/figures/` | Paper figures, audited hourly inputs, the extended 161-ratio sweep and three training-mean matrices |
| `manuscript/scripts/` | Figure-generation and table-checking scripts |
| `legacy-sampling/` | Earlier four-network source feasibility and protocol materials, including explicitly synthetic offline fixtures |
| `delivery_manifest.json` | Checksums of the packaged research artifacts |

The block gzip files and calendar are byte-identical to the original delivery. The inherited Chinese documentation was translated into `data/docs` and removed from the current raw directory. Its original content remains in prior Git history and the supplied source folder. Original documentation included earlier network lists, quintile rules, and five-minute selection plans, which are distinguished from the current study in the English notes.

## Current design and interpretation

The archive contains 76 hourly files per network. The paper's probability analysis uses 72 shared dates, drawn as four weekdays and two weekend dates in each of twelve phases, with seed 20231116 and UTC 12:00 to 13:00 sampling. Two Dencun dates remain separate, while two Base-related dates are outside the current analysis.

The static matrix A is an assumed eight-module, twelve-edge topology. The weighted matrices W use real transaction counts, contract creations, and block bytes through fixed coefficients. They are dimensionless proxies. Per-network training quantiles determine normalization, 36 shared dates train each layout, and 36 held-out dates evaluate it. Real opcode traces, hardware traffic calibration, and RTL performance measurements remain future work.

At vertical cost ratio 1, two-layer mean modeled cost is lower than optimized planar cost by 5.59%, 4.82%, and 5.25% for Ethereum, OP Mainnet, and Arbitrum One. At ratios 2 and 4 the two-layer model costs more. These are communication-cost comparisons, not execution speedups.

The nine-block manifest is an earlier whole-period feasibility selection using all 76 dates. It does not drive the current weighted matrices. Historical four-network blocked-access reports and synthetic fixtures under `legacy-sampling` are retained as development records and are not current empirical results.

## Reproduce

From the repository root, create a Python 3 environment and install the recorded plotting/numerical versions:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r experiment/outputs/workload_weighted/requirements.txt
.venv/bin/python -m unittest discover -s experiment -p 'test_*.py' -v
./experiment/outputs/workload_weighted/reproduce.sh
```

The current experiment reads only local source files and enumerates all 40,320 assignments per grid. An existing compatible environment can be used with `PYTHON=/path/to/python`.

Rebuild the manuscript's data figures and full layout sweep:

```sh
.venv/bin/python manuscript/scripts/plot_workloads.py --source data/raw
.venv/bin/python manuscript/scripts/plot_workload_combined.py
.venv/bin/python manuscript/scripts/plot_transaction_mix_shared.py
.venv/bin/python scripts/rebuild_layout_figures.py
```

The last script copies the newly generated weighted inputs into the manuscript artifacts before plotting. `plot_eight_panels.py` builds the final two-row, four-column comparison. The six-panel sensitivity figure remains among experiment outputs but is described in prose in the current manuscript. Auxiliary older plots remain for provenance.

Compile `manuscript/samplepaper.tex` with the supplied LNCS class using a compatible LaTeX engine, for example `tectonic manuscript/samplepaper.tex`. The delivered PDF has 13 pages including references.

The original static-only pipeline is available separately:

```sh
python3 experiment/experiment.py --source data/raw
```

This writes the historical pilot outputs. RPC probing is an optional network operation and is not required to reproduce the local weighted results. Source hashes verify copy integrity rather than independently establish chain authenticity. No additional source-data license grant is asserted.
