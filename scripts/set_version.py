#!/usr/bin/env python3
"""Set ontology header metadata on evi.owl (used by release.sh)."""

from __future__ import annotations

import argparse
from datetime import date

from evi_release import OWL_PATH, previous_version, replace_ontology_header


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="Version to declare, e.g. 1.6")
    parser.add_argument(
        "--prior",
        default=None,
        help="Prior version (default: latest frozen version below this one)",
    )
    parser.add_argument(
        "--modified",
        default=date.today().isoformat(),
        help="dcterms:modified (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Write back to evi.owl (default)",
    )
    args = parser.parse_args()
    prior = args.prior if args.prior is not None else previous_version(args.version)
    text = OWL_PATH.read_text(encoding="utf-8")
    updated = replace_ontology_header(
        text, version=args.version, prior=prior, modified=args.modified
    )
    OWL_PATH.write_text(updated, encoding="utf-8")
    print(f"Updated {OWL_PATH} to version {args.version} (prior {prior})")


if __name__ == "__main__":
    main()
