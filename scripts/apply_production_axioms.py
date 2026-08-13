#!/usr/bin/env python3
"""Apply one-time production axiom cleanup to the current evi.owl.

Safe to re-run: each replacement is idempotent.
Does not bump the version header — use set_version.py for that.
"""

from __future__ import annotations

import re

from evi_release import OWL_PATH, PROV_HTTPS, PROV_HTTP


def apply(text: str) -> str:
    # Canonical PROV namespace is http, not https.
    text = text.replace(PROV_HTTPS, PROV_HTTP)

    # Protege artifact: owl:versionIRI redeclared as an annotation property,
    # plus a second literal versionIRI pointing at the OWL namespace.
    text = re.sub(
        r"\n\s*<!-- http://www.w3.org/2002/07/owl#versionIRI -->\s*"
        r"<owl:AnnotationProperty rdf:about=\"http://www.w3.org/2002/07/owl#versionIRI\"/>\s*",
        "\n",
        text,
    )

    # xmlns:evi should include the hash used as the term namespace.
    text = text.replace(
        'xmlns:evi="https://w3id.org/EVI"',
        'xmlns:evi="https://w3id.org/EVI#"',
    )

    # SoftwareApplication / SoftwareSourceCode must not be equivalent to Software
    # (that would collapse the two schema.org types).
    text = text.replace(
        """    <owl:Class rdf:about="http://schema.org/SoftwareApplication">
        <owl:equivalentClass rdf:resource="https://w3id.org/EVI#Software"/>
        <rdfs:subClassOf rdf:resource="https://w3id.org/EVI#DigitalObject"/>
""",
        """    <owl:Class rdf:about="http://schema.org/SoftwareApplication">
        <rdfs:subClassOf rdf:resource="https://w3id.org/EVI#Software"/>
""",
    )
    text = text.replace(
        """    <owl:Class rdf:about="http://schema.org/SoftwareSourceCode">
        <owl:equivalentClass rdf:resource="https://w3id.org/EVI#Software"/>
        <rdfs:subClassOf rdf:resource="https://w3id.org/EVI#DigitalObject"/>
""",
        """    <owl:Class rdf:about="http://schema.org/SoftwareSourceCode">
        <rdfs:subClassOf rdf:resource="https://w3id.org/EVI#Software"/>
""",
    )

    # used / generatedBy run through Activities, so supports cannot be
    # DigitalObject-only without making those subproperties unsatisfiable.
    text = text.replace(
        """    <owl:ObjectProperty rdf:about="https://w3id.org/EVI#supports">
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#TransitiveProperty"/>
        <rdfs:domain rdf:resource="https://w3id.org/EVI#DigitalObject"/>
        <rdfs:range rdf:resource="https://w3id.org/EVI#DigitalObject"/>
        <rdfs:comment>The supports property is a transitive relation between DigitalObjects entailed by its subproperty, directlySupports, which is non-transitive. In EvidenceGraphs, if A supports B, then the correctness (truth value) of A provides a warrant for belief in the correctness (truth value) of B.</rdfs:comment>
        <rdfs:label>supports</rdfs:label>
    </owl:ObjectProperty>
""",
        """    <owl:ObjectProperty rdf:about="https://w3id.org/EVI#supports">
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#TransitiveProperty"/>
        <rdfs:comment>The supports property is a transitive relation entailed by its non-transitive subproperty directlySupports. Typical nodes are DigitalObjects; provenance shortcuts (used, generatedBy, createdBy, associatedWith) also participate so warrant can propagate through Activities and Agents. If A supports B, the correctness of A is a warrant for belief in the correctness of B.</rdfs:comment>
        <rdfs:label>supports</rdfs:label>
    </owl:ObjectProperty>
""",
    )

    text = text.replace(
        """    <owl:ObjectProperty rdf:about="https://w3id.org/EVI#supportedBy">
        <owl:inverseOf rdf:resource="https://w3id.org/EVI#supports"/>
        <rdfs:comment>The supportedBy property is a transitive relation between DigitalObjects.</rdfs:comment>
        <rdfs:label>supportedBy</rdfs:label>
    </owl:ObjectProperty>
""",
        """    <owl:ObjectProperty rdf:about="https://w3id.org/EVI#supportedBy">
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#TransitiveProperty"/>
        <owl:inverseOf rdf:resource="https://w3id.org/EVI#supports"/>
        <rdfs:comment>Inverse of supports. Transitive, matching supports.</rdfs:comment>
        <rdfs:label>supportedBy</rdfs:label>
    </owl:ObjectProperty>
""",
    )

    # createdBy: two rdfs:domain axioms mean intersection. Keep the super-class.
    text = text.replace(
        """        <rdfs:domain rdf:resource="https://w3id.org/EVI#DigitalObject"/>
        <rdfs:domain rdf:resource="http://www.w3.org/ns/prov#Entity"/>
""",
        """        <rdfs:domain rdf:resource="http://www.w3.org/ns/prov#Entity"/>
""",
    )

    replacements = {
        "The property usedModel is a subproperty of used where domain is Computation and range is MLModel. This is common in fine-tuning or inference tasks.": "The property usedMLModel is a subproperty of used where domain is Computation and range is MLModel. This is common in fine-tuning or inference tasks.",
        "The date when the item was modifed last.": "The date when the item was last modified.",
        "Refenrece to the publications where the item or its relevant information can be discovered.": "Reference to the publications where the item or its relevant information can be discovered.",
        "classificatoin": "classification",
        "interpretibility": "interpretability",
        "Cayrol &amp;amp; Lagasquie-Schiex": "Cayrol &amp; Lagasquie-Schiex",
        "where Rn is a set of Representations, r+ ∈ RnXRn is a set of supports relations, r- ∈ RnXRn is a set of challenge relations, and R+∩R- = Φ.": "where Rn is a set of DigitalObjects (and the Activities or Agents that warrant them), r+ is a set of supports relations, r- is a set of challenge relations, and r+ ∩ r- = ∅.",
        "A descriptive recipe describing how a Representation is made or obtained. It describes an Activity, and may referTo some Material as a component of the recipe.": "A descriptive recipe describing how a DigitalObject is made or obtained. It describes an Activity and may refer to other DigitalObjects or entities as components of the recipe.",
        "directlySupports is a superproperty of the properties attributed (inverse of attributedTo), derived (inverse of derivedFrom), associated (inverse of associatedWith), used, and generated (inverse of generatedBy).": "directlySupports is a superproperty of created (inverse of createdBy), derivedTo (inverse of derivedFrom), associateFor (inverse of associatedWith), usedBy (inverse of used), and generated (inverse of generatedBy).",
        "A Service is an Activity accessed online, which executes a Computation.": "A Service is a SoftwareAgent accessed online that executes a Computation.",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    # Label creator individuals.
    text = text.replace(
        """    <owl:NamedIndividual rdf:about="https://orcid.org/0000-0003-4060-7360"/>
""",
        """    <owl:NamedIndividual rdf:about="https://orcid.org/0000-0003-4060-7360">
        <rdfs:label>Timothy Clark</rdfs:label>
    </owl:NamedIndividual>
""",
    )
    text = text.replace(
        """    <owl:NamedIndividual rdf:about="https://orcid.org/0000-0003-4647-3877"/>
""",
        """    <owl:NamedIndividual rdf:about="https://orcid.org/0000-0003-4647-3877">
        <rdfs:label>Sadnan Al Manir</rdfs:label>
    </owl:NamedIndividual>
""",
    )
    return text


def main() -> None:
    original = OWL_PATH.read_text(encoding="utf-8")
    updated = apply(original)
    if updated == original:
        print("No axiom changes needed")
        return
    OWL_PATH.write_text(updated, encoding="utf-8")
    print(f"Applied production axioms to {OWL_PATH}")


if __name__ == "__main__":
    main()
