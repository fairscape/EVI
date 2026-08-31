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
    spec = (dest / "index.html").read_text(encoding="utf-8")
    assert "primer.js" not in spec
    assert not (dest / "primer.js").exists()
    assert not (dest / "reference").exists()
    assert f"versions/v{version}/" in spec
    assert 'href="https://orcid.org/0000-0003-4647-3877">Sadnan' in spec
    assert "what evidence currently bears on its correctness" in spec
    assert 'href="evi.owl"' in spec
    assert "github.com/fairscape/EVI" in spec
    assert (dest / "examples" / "smith-preterm.ttl").exists()
    assert (dest / "evi.owl").exists()
    assert (dest / "versions" / "v1.4" / "evi.owl").exists()
    assert (dest / "versions" / f"v{version}" / "evi.owl").exists()
    fig = dest / "resources" / "images" / f"v{version.replace('.', '')}"
    assert fig.is_dir()
    assert any(fig.glob("*.svg"))
    v14 = (dest / "versions" / "v1.4" / "evi.owl").read_text(encoding="utf-8")
    assert extract_version_info(v14) == "1.4"
