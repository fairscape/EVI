"""The teaching example must parse and use only terms that exist in evi.owl."""

from __future__ import annotations

from pathlib import Path

from rdflib import Graph, URIRef

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "smith-preterm.ttl"
OWL = ROOT / "evi.owl"


def test_smith_example_parses() -> None:
    graph = Graph()
    graph.parse(EXAMPLE, format="turtle")
    assert len(graph) > 20


def test_smith_example_uses_only_defined_evi_terms() -> None:
    ont = Graph()
    ont.parse(OWL, format="xml")
    defined = {s for s in ont.subjects() if str(s).startswith("https://w3id.org/EVI#")}

    data = Graph()
    data.parse(EXAMPLE, format="turtle")
    unknown = []
    for term in list(data.predicates()) + list(data.objects()):
        if isinstance(term, URIRef) and str(term).startswith("https://w3id.org/EVI#"):
            if term not in defined:
                unknown.append(str(term))
    assert unknown == [], f"Example uses terms not in evi.owl: {unknown}"


def test_smith_example_has_the_core_story() -> None:
    data = Graph()
    data.parse(EXAMPLE, format="turtle")
    text = EXAMPLE.read_text(encoding="utf-8")
    for needle in (
        "evi:Dataset",
        "evi:Computation",
        "evi:Software",
        "evi:Claim",
        "evi:Article",
        "evi:usedDataset",
        "evi:usedSoftware",
        "evi:directlyChallenges",
    ):
        assert needle in text
    assert len(data) > 0
