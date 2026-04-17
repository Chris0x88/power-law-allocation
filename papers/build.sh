#!/usr/bin/env bash
# Build papers from markdown to PDF using pandoc + tectonic.
#
# Requirements:
#   brew install pandoc tectonic
#
# Usage:
#   ./papers/build.sh              # build all papers
#   ./papers/build.sh thermal_stability.md
set -euo pipefail

cd "$(dirname "$0")"

build_one() {
  local md="$1"
  local pdf="${md%.md}.pdf"
  echo "→ $md → $pdf"
  pandoc "$md" \
    --from=markdown \
    --to=pdf \
    --pdf-engine=tectonic \
    --citeproc \
    --bibliography=references.bib \
    --number-sections=false \
    --highlight-style=tango \
    --metadata=link-citations:true \
    --output="$pdf"
  echo "  ✓ wrote $pdf"
}

if [[ $# -gt 0 ]]; then
  for f in "$@"; do build_one "$f"; done
else
  for f in thermal_stability.md; do
    [[ -f "$f" ]] && build_one "$f"
  done
fi
