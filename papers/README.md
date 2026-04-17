# Papers

Research papers supporting the power-law allocation framework.

## Canonical paper

- **[thermal_stability.md](thermal_stability.md)** — *Bitcoin's Journey Toward Thermal Stability: A Phenomenological Framework for Cycle-Aware Portfolio Allocation.* Working paper v2.0, April 2026.
- **[thermal_stability.pdf](thermal_stability.pdf)** — Rendered PDF (built from the markdown via pandoc + tectonic).

## Earlier internal papers

- [heartbeat_v3_paper.md](heartbeat_v3_paper.md) — V3 development paper (tax analysis, margin analysis, walk-forward)
- [heartbeat_v3.2_paper.md](heartbeat_v3.2_paper.md) — V3.2 refinement paper (continuous ceiling, asymmetric pulse, 22% threshold)
- [Bitcoins_Journey_Toward_Thermal_Stability_v1.pdf](Bitcoins_Journey_Toward_Thermal_Stability_v1.pdf) — archived v1 of the canonical paper

## Building the PDF

Requires `pandoc` and `tectonic`:

```bash
brew install pandoc tectonic
./papers/build.sh thermal_stability.md
```

The build script uses:
- **pandoc** to convert markdown → LaTeX
- **tectonic** as the PDF engine (self-contained, auto-fetches LaTeX packages)
- **--citeproc** with **references.bib** for automatic citation rendering

Output: `thermal_stability.pdf` (~100 KB, 12 pages).

## Reproducing the results

All numerical claims in the paper are reproducible from the reference
implementation in [`src/power_law/`](../src/power_law/):

```bash
python examples/quickstart.py            # today's signal + 36-month projection
python scripts/generate_chart.py         # regenerate the hero chart
```
