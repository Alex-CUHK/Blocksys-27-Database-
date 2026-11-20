# Blocksys 2027: EVM Workloads and Layout Pilot

**Initiator:** [Alex-CUHK](https://github.com/Alex-CUHK)  
**Email:** alexus20568@gmail.com

This repository contains the supplied Ethereum Mainnet, Optimism and Arbitrum One block-level dataset and an initial architecture-level layout experiment.

## Files and attachments

| Path | Contents |
|---|---|
| `data/raw/` | Original SQD Portal dataset, copied without content changes; macOS `.DS_Store` files excluded |
| `data/manifest.json` | File paths, byte sizes and SHA256 checksums for all source files |
| `experiment/EXPERIMENT_REPORT.txt` | English experiment report, limitations and reproduction instructions |
| `experiment/outputs/connection_matrix.txt` | Human-readable assumed hardware connection matrix |
| `experiment/outputs/architecture.json` | Module ordering and machine-readable adjacency matrix |
| `experiment/outputs/samples.json` | Nine candidate blocks, source hashes and trace-required status |
| `experiment/outputs/static_layout.json` | Baseline 2D, optimized 2D and 3D sensitivity results |
| `experiment/outputs/source_audit.json` | Source file and block-record counts |
| `experiment/outputs/rpc_probe.json` | Public RPC capability-probe responses |
| `experiment/experiment.py` | Sampling, assumed topology, exhaustive placement and event-matrix code |
| `experiment/probe_rpc.py` | Bounded, read-only public RPC capability probe |
| `experiment/test_experiment.py` | Four model and input-validation checks |

The original source documentation is retained in its original language for provenance. It contains inherited references to other chains and sampling designs; the actual uploaded directories are authoritative for included chains. This repository contains 76 compressed block files per chain, 228 in total. Original documentation is not an independently validated specification.

## Reproduce

Requires Python 3 with only the standard library. From the repository root:

```sh
python3 experiment/experiment.py --source data/raw
python3 -m unittest discover -s experiment -p 'test_*.py' -v
```

The sampling command reads the full dataset. The layout solver enumerates 40,320 placements for each grid/cost scenario. RPC probing is separate and requires network access and system curl:

```sh
python3 experiment/probe_rpc.py
```

## Interpretation

The connection matrix is a manually assumed eight-module architecture, not connectivity extracted from blockchain data or an RTL netlist. Layout costs are model units, not EVM speedups. The data provides block headers and receipt-derived aggregates, not execution traces. Real-workload communication mapping and cycle-level evaluation remain unimplemented.

The nine candidate blocks are a small pipeline pilot, not a representative estimate of the three-year population. Source hashes establish copy integrity, not independent blockchain authenticity. No license grant beyond existing source rights is asserted by this upload.
