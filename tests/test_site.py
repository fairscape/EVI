from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from assemble_site import assemble  # noqa: E402
from evi_release import extract_version_info  # noqa: E402


def test_assemble_site(tmp_path: Path) -> None:
    dest = tmp_path / "site"
    version = assemble(dest)
    current = extract_version_info((ROOT / "evi.owl").read_text(encoding="utf-8"))
    assert version == current
    assert (dest / "index.html").exists()
    primer = (dest / "index.html").read_text(encoding="utf-8")
    assert "primer.js" in primer
    assert "examples/smith-preterm.ttl" in primer
    assert "treats that provenance as evidence" in primer
    assert (dest / "primer.js").exists()
    assert (dest / "examples" / "smith-preterm.ttl").exists()

    spec = (dest / "reference" / "index.html").read_text(encoding="utf-8")
    assert f"versions/v{version}/" in spec
    assert 'href="https://orcid.org/0000-0003-4647-3877">Sadnan' in spec
    assert "treats that provenance as evidence" in spec
    assert (dest / "evi.owl").exists()
    assert (dest / "versions" / "v1.4" / "evi.owl").exists()
    assert (dest / "versions" / f"v{version}" / "evi.owl").exists()
    fig = dest / "resources" / "images" / f"v{version.replace('.', '')}"
    assert fig.is_dir()
    assert any(fig.glob("*.svg"))
    v14 = (dest / "versions" / "v1.4" / "evi.owl").read_text(encoding="utf-8")
    assert extract_version_info(v14) == "1.4"
