# How to publish a new EVI version

Humans do three things: edit the OWL, refresh the figure (or copy the last one), run `scripts/release.sh`. CI does the rest.

## Every time

1. Branch from `master`. Edit only `evi.owl` (and, if the diagram changed, `docs/figures/vNEXT/`).
2. `./scripts/release.sh 1.7`  
   Use `--copy-figure` when the class diagram is unchanged (license, comments, datatype tweaks).
3. Confirm `pytest` is green and `Ontology/versions/v1.7/evi.owl` is new.
4. Commit. Tag `v1.7`. Push the commit and the tag when you are ready to publish.
5. The `publish` workflow builds `site/` and updates `gh-pages`.
6. Optional: upload the new OWL to BioPortal; open a perma-id PR only if `docs/w3id.htaccess.example` changed.

## Never

- Edit `Ontology/versions/v*` for a version that already exists.
- Commit to `gh-pages` by hand.
- Change term IRIs (`https://w3id.org/EVI#…`) without a new major version and a migration note.

## Figure

Source files live in `docs/figures/vX.Y/` (`.drawio` plus exported `.svg` / `.png`). Copy the previous folder, open the `.drawio` in diagrams.net, export SVG, keep the version in the filename (`EVI-v-1-7.svg`).
