# Publishing a new version

1. Edit `evi.owl` in Protégé. If the class diagram changed, update `docs/figures/vNEXT/`.
2. `./scripts/release.sh 1.7`  
   Use `--copy-figure` when the drawing is unchanged.
3. Commit. Tag `v1.7`. Push the tag to publish https://fairscape.github.io/EVI/

Do not edit `Ontology/versions/v*` for a version that already exists. Do not commit to `gh-pages` by hand.

If you change a term used in [`examples/smith-preterm.ttl`](../examples/smith-preterm.ttl), update that file in the same commit. Tests fail if the example uses a term that is not in `evi.owl`.
