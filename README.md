# EVI: Evidence Graph Ontology

Scientific claims are not facts. They are assertions backed by evidence, and that evidence can be challenged. EVI is a small OWL vocabulary for writing that structure down: a dataset, the software and computation that produced a result, the claim, the article, and later challenges (a retracted paper, a bug in a library, a contaminated reagent).

It extends [PROV-O](https://www.w3.org/TR/prov-o/) and [Schema.org](https://schema.org/). Current version is **1.6** ([CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)).

- Specification: https://fairscape.github.io/EVI/
- Ontology: [`evi.owl`](evi.owl) · `https://w3id.org/EVI`
- Contact: Sadnan Al Manir (ma3xy@virginia.edu), Tim Clark (twclark@virginia.edu)

## A worked example

Mary Smith correlates post-menstrual age with birth weight in a preterm cohort. The computation uses SciPy 1.5.2. A later SciPy release challenges that software; the challenge sits under the same evidence graph as her claim.

Full file: [`examples/smith-preterm.ttl`](examples/smith-preterm.ttl) (valid Turtle; CI checks it against `evi.owl`).

```turtle
@prefix :     <https://example.org/evi/smith/> .
@prefix evi:  <https://w3id.org/EVI#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix schema: <http://schema.org/> .

:Mary_Smith a prov:Person .

:dataset_cohort a evi:Dataset ;
    evi:createdBy :Mary_Smith .

:computation_corr a evi:Computation ;
    evi:associatedWith :Mary_Smith ;
    evi:usedDataset :dataset_cohort ;
    evi:usedSoftware :software_pearsonr_152 ;
    evi:generated :dataset_corr .

:claim_pma_bw a evi:Claim ;
    evi:state "Post-conception age was significantly correlated with birth weight." ;
    evi:derivedFrom :dataset_corr .

:article_preprint a evi:Article ;
    evi:createdBy :Mary_Smith ;
    evi:contains :claim_pma_bw .

:software_pearsonr_160 a evi:Software ;
    schema:version "1.6.0" ;
    evi:directlyChallenges :software_pearsonr_152 .
```

`used` / `generatedBy` are subproperties of support, so warrant (and a challenge to the software) can propagate toward the claim.

## Maintainers

Edit `evi.owl` in Protégé. To freeze a version: `./scripts/release.sh 1.7` (or `--copy-figure` if the diagram is unchanged). That writes `Ontology/versions/v1.7/`, runs tests, and refuses to overwrite an older snapshot. Tag `v1.7` to publish the docs site. Do not edit `gh-pages` or existing version folders by hand.

Details: [`docs/RELEASE.md`](docs/RELEASE.md) · [`CHANGELOG.md`](CHANGELOG.md)
