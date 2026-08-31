# Changelog

## 1.6 — 2026-08-13

Production cleanup. No new classes.

- Restore the v1.4 snapshot (it had been overwritten with 1.5 metadata).
- Single `owl:versionIRI` (`https://w3id.org/EVI/1.6`); drop the Protege annotation that pointed at the OWL namespace.
- Namespace: `vann:preferredNamespaceUri` is `https://w3id.org/EVI#`.
- Canonical PROV IRIs (`http://www.w3.org/ns/prov#`).
- `schema:SoftwareApplication` and `schema:SoftwareSourceCode` are subclasses of `evi:Software`, not equivalent to it.
- `supports` / `supportedBy` no longer force DigitalObject-only domain and range (so `used` / `generatedBy` through Activities stay coherent). `supportedBy` is transitive.
- Creator ORCIDs labelled; comments and typos fixed.
- Release automation, version-integrity tests, generated documentation site.
- Teaching example: `examples/smith-preterm.ttl` (checked in CI). Dataset + schema + computation; no Claim/Article.
- Abstract updated for 1.6. The specification is the documentation homepage. The version number remains 1.6.

## 1.5 — 2026-04-25

Relicense to [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Vocabulary unchanged from 1.4.

## 1.4 — 2026-03-18

`Document`, `Annotation`, `annotates`. `annotates` range narrowed to `DigitalObject`.

## 1.3 — 2025-12-05

`Experiment`, `Instrument`, `Reagent`, `Sample` and typed `used*` properties. `hasSchema` / `schemaFor`.

## 1.2 — 2025-11-13

`MLModel`, `Package`, `ROCrate`, `usedMLModel`, MLModel datatype properties.

## 1.1 — 2023-05-15

`Container`, `packages` / `packagedBy`.

## 1.0 — 2023-05-06

`DigitalObject` core. Dropped `Representation`, `Material`, `Identifier`, `DataAcquisition`.

## 0.2 — 2020-09-09

Early public release.

## 0.1 — 2020-07-28

Initial alpha.
