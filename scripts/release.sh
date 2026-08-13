#!/usr/bin/env bash
# Freeze the current evi.owl as a new version and refresh derived artifacts.
# Human steps that remain: edit evi.owl, update the figure (or pass --copy-figure),
# then run this script, review, commit, and tag.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/scripts"

usage() {
  cat <<EOF
Usage: $0 <version> [--copy-figure] [--modified YYYY-MM-DD]

  Freeze evi.owl as Ontology/versions/v<version>/evi.owl, write serializations,
  and run integrity tests.

  --copy-figure   If docs/figures/v<version> is missing, copy the previous
                  version's figure folder (for license/metadata-only releases).
EOF
  exit 1
}

VERSION=""
COPY_FIGURE=0
MODIFIED=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --copy-figure) COPY_FIGURE=1; shift ;;
    --modified) MODIFIED="${2:-}"; shift 2 ;;
    -h|--help) usage ;;
    *)
      if [[ -z "$VERSION" ]]; then VERSION="$1"; shift
      else usage
      fi
      ;;
  esac
done
[[ -n "$VERSION" ]] || usage

if [[ ! -x "$ROOT/.venv/bin/python" ]]; then
  echo "Create a venv first: python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt" >&2
  exit 1
fi
PY="$ROOT/.venv/bin/python"

VERSION="$("$PY" -c "from evi_release import parse_version; print(parse_version('$VERSION'))")"
DEST="$ROOT/Ontology/versions/v${VERSION}"
if [[ -e "$DEST" ]]; then
  echo "Refusing to overwrite existing snapshot $DEST" >&2
  exit 1
fi

FIG="$ROOT/docs/figures/v${VERSION}"
if [[ ! -d "$FIG" ]]; then
  if [[ "$COPY_FIGURE" -eq 1 ]]; then
    PRIOR="$("$PY" -c "from evi_release import previous_version; print(previous_version('$VERSION') or '')")"
    if [[ -z "$PRIOR" || ! -d "$ROOT/docs/figures/v${PRIOR}" ]]; then
      echo "No previous figure folder to copy (looked for docs/figures/v${PRIOR:-?})" >&2
      exit 1
    fi
    mkdir -p "$FIG"
    cp -R "$ROOT/docs/figures/v${PRIOR}/." "$FIG/"
    echo "Copied figures from v${PRIOR} -> v${VERSION}"
  else
    echo "Missing $FIG" >&2
    echo "Add a semantic-model figure, or re-run with --copy-figure" >&2
    exit 1
  fi
fi

SET_ARGS=("$VERSION")
if [[ -n "$MODIFIED" ]]; then
  SET_ARGS+=(--modified "$MODIFIED")
fi
"$PY" "$ROOT/scripts/set_version.py" "${SET_ARGS[@]}"

mkdir -p "$DEST"
cp "$ROOT/evi.owl" "$DEST/evi.owl"
echo "Froze $DEST/evi.owl"

"$PY" "$ROOT/scripts/serialize.py"
"$PY" -m pytest "$ROOT/tests" -q
echo
echo "Release $VERSION is ready locally."
echo "  1. Review git diff"
echo "  2. git add -A && git commit -m \"Release EVI $VERSION\""
echo "  3. git tag v$VERSION"
echo "  4. After you push the tag, CI publishes gh-pages"
echo "Do not edit Ontology/versions/v* for older versions."
