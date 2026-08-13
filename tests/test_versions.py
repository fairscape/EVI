"""Integrity checks that would have caught the v1.4 / v1.5 overwrite."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest
from rdflib import OWL, RDF, RDFS, Graph, URIRef

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from evi_release import (  # noqa: E402
    NS,
    OWL_PATH,
    VERSIONS_DIR,
    extract_version_info,
    extract_version_iri_resource,
    latest_frozen_version,
    parse_version,
)

PROV = "http://www.w3.org/ns/prov#"
PROV_HTTPS = "https://www.w3.org/ns/prov#"


def _version_dirs() -> list[tuple[str, Path]]:
    found = []
    for path in VERSIONS_DIR.iterdir():
        owl = path / "evi.owl"
        if path.is_dir() and owl.exists():
            found.append((parse_version(path.name), owl))
    return sorted(found, key=lambda item: tuple(int(p) for p in item[0].split(".")))


def test_every_snapshot_declares_its_folder_version() -> None:
    mismatches = []
    for version, owl in _version_dirs():
        info = extract_version_info(owl.read_text(encoding="utf-8"))
        if info != version:
            mismatches.append(f"{owl.parent.name}: versionInfo={info!r}")
    assert mismatches == [], "Snapshot identity mismatch:\n" + "\n".join(mismatches)


def test_snapshots_are_unique_files() -> None:
    by_hash: dict[str, list[str]] = {}
    for version, owl in _version_dirs():
        digest = owl.read_bytes()
        by_hash.setdefault(digest, []).append(version)
    dupes = {k: v for k, v in by_hash.items() if len(v) > 1}
    assert not dupes, f"Identical snapshots: {list(dupes.values())}"


def test_current_owl_matches_latest_snapshot() -> None:
    latest = latest_frozen_version()
    assert latest is not None
    current = OWL_PATH.read_text(encoding="utf-8")
    frozen = (VERSIONS_DIR / f"v{latest}" / "evi.owl").read_text(encoding="utf-8")
    assert extract_version_info(current) == latest
    assert current == frozen


def test_prior_version_chain() -> None:
    versions = [v for v, _ in _version_dirs()]
    for prev, curr in zip(versions, versions[1:]):
        text = (VERSIONS_DIR / f"v{curr}" / "evi.owl").read_text(encoding="utf-8")
        # 1.6+ uses rdf:resource; older snapshots use a literal.
        if re.search(rf'priorVersion rdf:resource="https://w3id.org/EVI/{re.escape(prev)}"', text):
            continue
        if re.search(rf"<owl:priorVersion[^>]*>{re.escape(prev)}</owl:priorVersion>", text):
            continue
        if curr == versions[0]:
            continue
        pytest.fail(f"{curr} does not declare priorVersion {prev}")


def test_current_header_is_clean() -> None:
    text = OWL_PATH.read_text(encoding="utf-8")
    latest = latest_frozen_version()
    assert extract_version_iri_resource(text) == f"https://w3id.org/EVI/{latest}"
    assert 'owl:versionIRI xml:lang="en">http://www.w3.org/2002/07/owl' not in text
    assert 'rdf:about="http://www.w3.org/2002/07/owl#versionIRI"' not in text
    assert 'preferredNamespaceUri rdf:resource="https://w3id.org/EVI#"' in text


def test_current_uses_canonical_prov_namespace() -> None:
    text = OWL_PATH.read_text(encoding="utf-8")
    assert PROV_HTTPS not in text
    assert f"{PROV}Entity" in text
    assert f"{PROV}SoftwareAgent" in text


def test_current_parses_as_rdf() -> None:
    graph = Graph()
    graph.parse(OWL_PATH, format="xml")
    assert (URIRef("https://w3id.org/EVI"), RDF.type, OWL.Ontology) in graph
    supports = URIRef(f"{NS}supports")
    supported_by = URIRef(f"{NS}supportedBy")
    assert (supports, RDF.type, OWL.TransitiveProperty) in graph
    assert (supported_by, RDF.type, OWL.TransitiveProperty) in graph


def test_software_schema_types_are_not_equivalent() -> None:
    graph = Graph()
    graph.parse(OWL_PATH, format="xml")
    software = URIRef(f"{NS}Software")
    app = URIRef("http://schema.org/SoftwareApplication")
    src = URIRef("http://schema.org/SoftwareSourceCode")
    assert (app, OWL.equivalentClass, software) not in graph
    assert (src, OWL.equivalentClass, software) not in graph
    assert (app, RDFS.subClassOf, software) in graph
    assert (src, RDFS.subClassOf, software) in graph


def test_creators_are_labelled() -> None:
    graph = Graph()
    graph.parse(OWL_PATH, format="xml")
    sadnan = URIRef("https://orcid.org/0000-0003-4647-3877")
    tim = URIRef("https://orcid.org/0000-0003-4060-7360")
    labels = {str(o) for o in graph.objects(sadnan, RDFS.label)}
    assert "Sadnan Al Manir" in labels
    labels = {str(o) for o in graph.objects(tim, RDFS.label)}
    assert "Timothy Clark" in labels
