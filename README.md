# EVI: Evidence Graph Ontology

The Evidence Graph Ontology (EVI) is an OWL 2 vocabulary for recording how a biomedical result was produced and what evidence currently bears on its correctness.

It extends [PROV-O](https://www.w3.org/TR/prov-o/). Current version is **1.6** ([CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)).

- Specification: https://fairscape.github.io/EVI/
- Ontology: [`evi.owl`](evi.owl) · `https://w3id.org/EVI`
- Contact: Sadnan Al Manir (ma3xy@virginia.edu), Tim Clark (twclark@virginia.edu)

## A worked example

Mary Smith has a preterm cohort dataset (with a schema for its columns), runs SciPy on it, and gets a result table (also with a schema).

Full file: [`examples/smith-preterm.ttl`](examples/smith-preterm.ttl) (valid Turtle; CI checks it against `evi.owl`).

```turtle
@prefix :     <https://example.org/evi/smith/> .
@prefix evi:  <https://w3id.org/EVI#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix schema: <http://schema.org/> .

:Mary_Smith a prov:Person .

:schema_cohort a evi:Schema ;
    schema:description "subject_id, post_menstrual_age_days, sex, birth_weight_g." .

:dataset_cohort a evi:Dataset ;
    evi:createdBy :Mary_Smith ;
    evi:hasSchema :schema_cohort .

:computation_corr a evi:Computation ;
    evi:associatedWith :Mary_Smith ;
    evi:usedDataset :dataset_cohort ;
    evi:usedSoftware :software_pearsonr ;
    evi:generated :dataset_corr .

:dataset_corr a evi:Dataset ;
    evi:generatedBy :computation_corr ;
    evi:hasSchema :schema_results .
```

## Maintainers

Edit `evi.owl` in Protégé. To freeze a version: `./scripts/release.sh 1.7` (or `--copy-figure` if the diagram is unchanged). That writes `Ontology/versions/v1.7/`, runs tests, and refuses to overwrite an older snapshot. Tag `v1.7` to publish the docs site. Do not edit `gh-pages` or existing version folders by hand.

Details: [`docs/RELEASE.md`](docs/RELEASE.md) · [`CHANGELOG.md`](CHANGELOG.md)
