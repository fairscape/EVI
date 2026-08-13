#!/usr/bin/env python3
"""Serialize evi.owl to Turtle, N-Triples, RDF/XML, and JSON-LD."""

from __future__ import annotations

import argparse
from pathlib import Path

from rdflib import Graph

from evi_release import OWL_PATH, SERIAL_DIR


FORMATS = {
    "ttl": ("turtle", "evi.ttl"),
    "nt": ("nt", "evi.nt"),
    "rdf": ("pretty-xml", "evi.rdf"),
    "jsonld": ("json-ld", "evi.jsonld"),
}


def serialize(owl_path: Path, dest: Path) -> dict[str, Path]:
    graph = Graph()
    graph.parse(owl_path, format="xml")
    dest.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}
    for key, (fmt, name) in FORMATS.items():
        out = dest / name
        graph.serialize(destination=out, format=fmt)
        written[key] = out
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owl", type=Path, default=OWL_PATH)
    parser.add_argument("--dest", type=Path, default=SERIAL_DIR)
    args = parser.parse_args()
    written = serialize(args.owl, args.dest)
    for key, path in written.items():
        print(f"{key:7} {path} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
