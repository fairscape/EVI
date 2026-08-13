"""Shared helpers for EVI version metadata, serialization, and site assembly."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OWL_PATH = ROOT / "evi.owl"
VERSIONS_DIR = ROOT / "Ontology" / "versions"
FIGURES_DIR = ROOT / "docs" / "figures"
SERIAL_DIR = ROOT / "serializations"
SITE_DIR = ROOT / "site"
DOCS_DIR = ROOT / "docs"
EXAMPLES_DIR = ROOT / "examples"

ONTOLOGY_IRI = "https://w3id.org/EVI"
NS = "https://w3id.org/EVI#"
PROV_HTTP = "http://www.w3.org/ns/prov#"
PROV_HTTPS = "https://www.w3.org/ns/prov#"
LICENSE_CC_BY = "https://creativecommons.org/licenses/by/4.0/"

ORCID_SADNAN = "https://orcid.org/0000-0003-4647-3877"
ORCID_TIM = "https://orcid.org/0000-0003-4060-7360"

VERSION_RE = re.compile(r"^v?(\d+(?:\.\d+)*)$")


def parse_version(value: str) -> str:
    match = VERSION_RE.match(value.strip())
    if not match:
        raise ValueError(f"Invalid version: {value!r} (expected 1.6 or v1.6)")
    return match.group(1)


def folder_for(version: str) -> Path:
    return VERSIONS_DIR / f"v{parse_version(version)}"


def version_iri(version: str) -> str:
    return f"{ONTOLOGY_IRI}/{parse_version(version)}"


def previous_version(version: str) -> str | None:
    """Return the highest frozen version strictly below `version`."""
    target = _version_key(parse_version(version))
    found: list[tuple[tuple[int, ...], str]] = []
    if not VERSIONS_DIR.exists():
        return None
    for path in VERSIONS_DIR.iterdir():
        if not path.is_dir() or not (path / "evi.owl").exists():
            continue
        try:
            ver = parse_version(path.name)
        except ValueError:
            continue
        key = _version_key(ver)
        if key < target:
            found.append((key, ver))
    if not found:
        return None
    return max(found)[1]


def _version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def latest_frozen_version() -> str | None:
    if not VERSIONS_DIR.exists():
        return None
    found: list[tuple[tuple[int, ...], str]] = []
    for path in VERSIONS_DIR.iterdir():
        if path.is_dir() and (path / "evi.owl").exists():
            try:
                ver = parse_version(path.name)
            except ValueError:
                continue
            found.append((_version_key(ver), ver))
    return max(found)[1] if found else None


def extract_version_info(owl_text: str) -> str | None:
    match = re.search(
        r'<owl:versionInfo(?:\s[^>]*)?>([^<]+)</owl:versionInfo>',
        owl_text,
    )
    return match.group(1).strip() if match else None


def extract_version_iri_resource(owl_text: str) -> str | None:
    match = re.search(r'<owl:versionIRI rdf:resource="([^"]+)"', owl_text)
    return match.group(1) if match else None


def replace_ontology_header(
    owl_text: str,
    *,
    version: str,
    prior: str | None,
    modified: str,
    license_iri: str = LICENSE_CC_BY,
) -> str:
    """Replace the <owl:Ontology>...</owl:Ontology> block with a clean  header."""
    version = parse_version(version)
    prior_xml = (
        f'        <owl:priorVersion rdf:resource="{version_iri(prior)}"/>\n'
        f'        <owl:backwardCompatibleWith rdf:resource="{version_iri(prior)}"/>\n'
        if prior
        else ""
    )
    header = f"""    <owl:Ontology rdf:about="{ONTOLOGY_IRI}">
        <owl:versionIRI rdf:resource="{version_iri(version)}"/>
{prior_xml}        <owl:versionInfo xml:lang="en">{version}</owl:versionInfo>
        <terms:title xml:lang="en">EVI: Evidence Graph Ontology</terms:title>
        <terms:description xml:lang="en">The Evidence Graph ontology extends core concepts from the W3C Provenance Ontology PROV-O, Schema.org, and Bioschemas' Profiles to describe evidence for correctness of findings in biomedical publications. The semantic data model in EVI is expressed using OWL2 Web Ontology Language (OWL2).</terms:description>
        <terms:created xml:lang="en">2020-07-27</terms:created>
        <terms:modified xml:lang="en">{modified}</terms:modified>
        <terms:license rdf:resource="{license_iri}"/>
        <terms:creator rdf:resource="{ORCID_SADNAN}"/>
        <terms:creator rdf:resource="{ORCID_TIM}"/>
        <terms:contributor rdf:resource="https://github.com/jniestroy"/>
        <terms:contributor rdf:resource="https://github.com/mlev71"/>
        <vann:preferredNamespacePrefix>evi</vann:preferredNamespacePrefix>
        <vann:preferredNamespaceUri rdf:resource="{NS}"/>
        <rdfs:seeAlso rdf:resource="https://fairscape.github.io/EVI/"/>
    </owl:Ontology>"""
    pattern = re.compile(
        r'    <owl:Ontology rdf:about="https://w3id.org/EVI">.*?</owl:Ontology>',
        re.S,
    )
    if not pattern.search(owl_text):
        raise ValueError("Could not find owl:Ontology block")
    return pattern.sub(header, owl_text, count=1)


def figure_dir(version: str) -> Path:
    return FIGURES_DIR / f"v{parse_version(version)}"


def find_figure(version: str) -> Path | None:
    directory = figure_dir(version)
    if not directory.is_dir():
        return None
    preferred = [
        directory / f"EVI-v-{parse_version(version).replace('.', '-')}.svg",
        directory / "EVI.svg",
    ]
    for path in preferred:
        if path.exists():
            return path
    svgs = sorted(directory.glob("*.svg"))
    return svgs[0] if svgs else None
