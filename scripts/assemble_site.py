#!/usr/bin/env python3
"""Build the static docs site under site/ from master sources."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

from evi_release import (
    DOCS_DIR,
    FIGURES_DIR,
    OWL_PATH,
    SERIAL_DIR,
    SITE_DIR,
    VERSIONS_DIR,
    extract_version_info,
    find_figure,
    folder_for,
    parse_version,
    previous_version,
)


def _copy(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
    else:
        shutil.copy2(src, dest)


def _legacy_image_dir(version: str) -> str:
    """Map 1.4 -> v14, 0.2 -> v02, matching the historical gh-pages layout."""
    parts = parse_version(version).split(".")
    if parts[0] == "0":
        return "v0" + "".join(parts[1:])
    return "v" + "".join(parts)


def _patch_index(html: str, version: str, prior: str | None, modified: str) -> str:
    html = re.sub(
        r"<h2>Release [^<]+</h2>",
        f"<h2>Release {modified}</h2>",
        html,
        count=1,
    )
    html = re.sub(
        r'(<dt>Current version:</dt>\s*<dd><a href=")[^"]+(">)[^<]+(</a>)',
        rf"\g<1>versions/v{version}/\g<2>{version}\g<3>",
        html,
        count=1,
    )
    if prior:
        html = re.sub(
            r'(<dt>Previous version:</dt>\s*<dd><a href=")[^"]+(">)[^<]+(</a>)',
            rf"\g<1>versions/v{prior}/\g<2>{prior}\g<3>",
            html,
            count=1,
        )
    if "Version archive:" not in html:
        html = html.replace(
            "<dt>Authors:</dt>",
            '<dt>Version archive:</dt>\n                <dd><a href="versions/">all published versions</a></dd>\n                <dt>Authors:</dt>',
            1,
        )
    html = html.replace(
        "https://orcid.org/0000-0003-4060-7360\">Sadnan Al Manir",
        "https://orcid.org/0000-0003-4647-3877\">Sadnan Al Manir",
    )
    # Keep Tim on 0000-0003-4060-7360 (already correct if Sadnan is fixed first).
    html = re.sub(
        r'"version":"[^"]+"',
        f'"version":"{version}"',
        html,
        count=1,
    )
    html = re.sub(
        r'"license":"http://creativecommons.org/licenses/by-nc-sa/2.0/"',
        '"license":"https://creativecommons.org/licenses/by/4.0/"',
        html,
        count=1,
    )
    figure = find_figure(version)
    if figure:
        dest = f"resources/images/{_legacy_image_dir(version)}/{figure.name}"
        html = re.sub(
            r'src="resources/images/v[0-9]+/[^"]+\.svg"',
            f'src="{dest}"',
            html,
            count=1,
        )
    return html


def _version_page(version: str, owl_text: str) -> str:
    info = extract_version_info(owl_text) or "—"
    iri = re.search(r'<owl:versionIRI rdf:resource="([^"]+)"', owl_text)
    license_m = re.search(r'<terms:license[^>]*>([^<]+)</terms:license>|<terms:license rdf:resource="([^"]+)"', owl_text)
    license_v = (license_m.group(1) or license_m.group(2)) if license_m else "—"
    modified_m = re.search(r'<terms:modified[^>]*>([^<]+)</terms:modified>', owl_text)
    modified = modified_m.group(1) if modified_m else "—"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>EVI {version}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem auto; max-width: 52rem; }}
    a {{ color: #1f3b5b; }}
  </style>
</head>
<body>
  <p><a href="../../index.html">Documentation</a> · <a href="../">All versions</a></p>
  <h1>EVI {version}</h1>
  <ul>
    <li>versionInfo: <strong>{info}</strong></li>
    <li>versionIRI: {iri.group(1) if iri else "—"}</li>
    <li>modified: {modified}</li>
    <li>license: {license_v}</li>
  </ul>
  <p><a href="evi.owl">Download evi.owl</a></p>
</body>
</html>
"""


def _archive_index(versions: list[str], current: str) -> str:
    items = "\n".join(
        f'    <li><a href="v{v}/">{"<strong>" if v == current else ""}{v}'
        f'{"</strong> (current)" if v == current else ""}</a></li>'
        for v in reversed(versions)
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>EVI versions</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem auto; max-width: 52rem; }}
  </style>
</head>
<body>
  <p><a href="../index.html">Documentation</a></p>
  <h1>Published versions</h1>
  <ul>
{items}
  </ul>
</body>
</html>
"""


def assemble(dest: Path) -> str:
    if not OWL_PATH.exists():
        raise SystemExit(f"missing {OWL_PATH}")
    owl_text = OWL_PATH.read_text(encoding="utf-8")
    version = extract_version_info(owl_text)
    if not version:
        raise SystemExit("evi.owl has no owl:versionInfo")
    prior = previous_version(version)
    modified_m = re.search(r'<terms:modified[^>]*>([^<]+)</terms:modified>', owl_text)
    modified = modified_m.group(1) if modified_m else ""

    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    template = DOCS_DIR / "templates" / "index.html"
    html = template.read_text(encoding="utf-8")
    (dest / "index.html").write_text(
        _patch_index(html, version, prior, modified), encoding="utf-8"
    )

    # Static assets
    for name in ("extra.css", "owl.css", "primer.css", "rec.css", "jquery.js", "marked.min.js"):
        src = DOCS_DIR / "assets" / name
        if src.exists():
            _copy(src, dest / "resources" / name)
    if (DOCS_DIR / "406.html").exists():
        _copy(DOCS_DIR / "406.html", dest / "406.html")
    htaccess = DOCS_DIR / "htaccess"
    if htaccess.exists():
        _copy(htaccess, dest / ".htaccess")

    # Figures: keep historical folders plus current
    if FIGURES_DIR.exists():
        for fig_dir in sorted(FIGURES_DIR.iterdir()):
            if not fig_dir.is_dir():
                continue
            try:
                ver = parse_version(fig_dir.name)
            except ValueError:
                continue
            _copy(fig_dir, dest / "resources" / "images" / _legacy_image_dir(ver))

    # Current OWL + serializations at site root (content negotiation targets)
    _copy(OWL_PATH, dest / "evi.owl")
    if SERIAL_DIR.exists():
        for name in ("evi.ttl", "evi.nt", "evi.rdf", "evi.jsonld"):
            src = SERIAL_DIR / name
            if src.exists():
                _copy(src, dest / name)
                # Aliases expected by older w3id rules
                alias = {
                    "evi.ttl": "ontology.ttl",
                    "evi.nt": "ontology.nt",
                    "evi.rdf": "ontology.xml",
                    "evi.jsonld": "ontology.json",
                }[name]
                _copy(src, dest / alias)

    # Frozen snapshots
    versions: list[str] = []
    if VERSIONS_DIR.exists():
        for path in sorted(VERSIONS_DIR.iterdir()):
            owl = path / "evi.owl"
            if not path.is_dir() or not owl.exists():
                continue
            try:
                ver = parse_version(path.name)
            except ValueError:
                continue
            versions.append(ver)
            target = dest / "versions" / f"v{ver}"
            target.mkdir(parents=True)
            _copy(owl, target / "evi.owl")
            (target / "index.html").write_text(
                _version_page(ver, owl.read_text(encoding="utf-8")),
                encoding="utf-8",
            )
    (dest / "versions" / "index.html").write_text(
        _archive_index(versions, version), encoding="utf-8"
    )

    # Ensure current freeze exists in site even before folder copy if missing
    current_folder = folder_for(version)
    if current_folder.exists():
        _copy(OWL_PATH, dest / "versions" / f"v{version}" / "evi.owl")

    return version


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", type=Path, default=SITE_DIR)
    args = parser.parse_args()
    version = assemble(args.dest)
    print(f"Assembled site for EVI {version} at {args.dest}")


if __name__ == "__main__":
    main()
