# EVI: Evidence Graph Ontology

EVI extends [PROV-O](https://www.w3.org/TR/prov-o/), [Schema.org](https://schema.org/), and [Bioschemas](https://bioschemas.org/profiles/) to describe **evidence for the correctness of findings** in biomedical research. Claims are treated as defeasible: support and challenge relations form a directed evidence graph.

| | |
|---|---|
| Ontology IRI | `https://w3id.org/EVI` |
| Current version | **1.6** (`https://w3id.org/EVI/1.6`) |
| License | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| Docs | https://fairscape.github.io/EVI/ |
| OWL | [`evi.owl`](evi.owl) |

Contact: Sadnan Al Manir (ma3xy@virginia.edu), Tim Clark (twclark@virginia.edu).

## Repository layout

```
evi.owl                      current ontology (edit this)
Ontology/versions/vX.Y/      frozen snapshots — never edit after release
docs/figures/vX.Y/           semantic-model figure for that version
docs/templates/index.html    documentation page (WIDOCO-based)
scripts/release.sh           freeze a version + serialize + test
.github/workflows/           validate on PR; publish gh-pages on tag
```

`gh-pages` is generated. Do not hand-edit it.

## Edit and release

1. Change `evi.owl` (Protégé or a text editor).
2. Update `docs/figures/v<new>/` from the previous `.drawio`, **or** skip a new drawing and pass `--copy-figure`.
3. Freeze:

   ```bash
   python3 -m venv .venv
   .venv/bin/pip install -r requirements-dev.txt
   ./scripts/release.sh 1.7            # or: ./scripts/release.sh 1.7 --copy-figure
   ```

   That script refuses to overwrite an existing `Ontology/versions/v1.7/`, writes serializations, and runs the tests that require each snapshot’s `versionInfo` to match its folder name.

4. Review, commit, tag `v1.7`. Pushing the tag publishes the site. Do not push until you intend to.

Older `Ontology/versions/v*` files are immutable. The v1.4 folder was once overwritten in place; tests now fail if that happens again.

## Local docs preview

```bash
make site
python3 -m http.server 8770 --directory site
```

Then open http://127.0.0.1:8770/ — Current / Previous version, the figure, and `/versions/` are local.

## Version IRIs

After the site is published, [w3id.org/EVI](https://github.com/perma-id/w3id.org/tree/master/EVI) should redirect `https://w3id.org/EVI/1.6` to this repo’s snapshot. A ready-to-submit rules file is [`docs/w3id.htaccess.example`](docs/w3id.htaccess.example). That change lives in the perma-id repository, not here.
