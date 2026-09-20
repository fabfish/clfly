"""Fetch the connectome substrate.

The data is **never redistributed** by this repository.  This script clones it
from its distributors into ``data/`` (gitignored) and records the exact commit
hash of each clone, so a result can always be traced back to the bytes that
produced it.

Sources, both open and both verified reachable from this environment:

``philshiu/Drosophila_brain_model`` (MIT)
    Ships ``Connectivity_783.parquet`` (~100 MB) and ``Completeness_783.csv``:
    the FlyWire v783 proofread connectivity in a form ready to load.  The
    repository's own README confirms these ship in-repo -- only the multi-GB
    raw simulation output is hosted elsewhere.

``flyconnectome/flywire_annotations``
    ``supplemental_files/Supplemental_file1_neuron_annotations.tsv``: one row
    per neuron with flow, superclass, cell class, nerve, lineage, side,
    morphology group, neurotransmitter and VFB id.  This is where the candidate
    anchoring bases come from -- see :mod:`clfly.lgcl.bases`.

Note on transport: ``raw.githubusercontent.com`` is unreachable from the
environment this was developed in, so everything goes through ``git clone``.
That is also the more robust choice in general.

    python -m clfly.connectome.fetch            # clone whatever is missing
    python -m clfly.connectome.fetch --check    # report status only
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = REPO_ROOT / "data"


@dataclass(frozen=True)
class Source:
    key: str
    url: str
    licence: str
    note: str


SOURCES = (
    Source(
        key="drosophila_brain_model",
        url="https://github.com/philshiu/Drosophila_brain_model",
        licence="MIT (code); FlyWire connectivity inherits CC BY-NC 4.0",
        note="FlyWire v783 connectivity parquet + neuron completeness list",
    ),
    Source(
        key="flywire_annotations",
        url="https://github.com/flyconnectome/flywire_annotations",
        licence="FlyWire annotations, CC BY-NC 4.0",
        note="per-neuron cell type / class / hemilineage / nerve annotations",
    ),
)


def _run(cmd: list[str], cwd: Path | None = None) -> str:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)} failed:\n{proc.stderr.strip()}")
    return proc.stdout.strip()


def head_commit(path: Path) -> str | None:
    """Return the cloned commit hash, or ``None`` if ``path`` is not a repo."""
    if not (path / ".git").exists():
        return None
    try:
        return _run(["git", "rev-parse", "HEAD"], cwd=path)
    except RuntimeError:
        return None


def fetch_source(src: Source, data_dir: Path = DEFAULT_DATA_DIR, quiet: bool = False) -> Path:
    """Shallow-clone ``src`` into ``data_dir`` if it is not already there."""
    dest = data_dir / src.key
    if head_commit(dest):
        if not quiet:
            print(f"  {src.key}: already present @ {head_commit(dest)[:12]}")
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not quiet:
        print(f"  {src.key}: cloning {src.url} ...")
    _run(["git", "clone", "--depth", "1", src.url, str(dest)])
    if not quiet:
        print(f"  {src.key}: done @ {head_commit(dest)[:12]}")
    return dest


def verify(data_dir: Path = DEFAULT_DATA_DIR) -> dict:
    """Check that the files we actually need are where we expect them."""
    expected = {
        "drosophila_brain_model": [
            "Connectivity_783.parquet",
            "Completeness_783.csv",
        ],
        "flywire_annotations": [
            "supplemental_files/Supplemental_file1_neuron_annotations.tsv",
        ],
    }
    report = {}
    for key, rels in expected.items():
        base = data_dir / key
        present = {}
        for rel in rels:
            p = base / rel
            present[rel] = p.stat().st_size if p.exists() else None
        report[key] = {
            "commit": head_commit(base),
            "files": present,
            "ok": all(v is not None for v in present.values()),
        }
    return report


def ensure(data_dir: Path = DEFAULT_DATA_DIR, quiet: bool = False) -> dict:
    """Clone everything missing, then verify and write a provenance manifest."""
    data_dir.mkdir(parents=True, exist_ok=True)
    for src in SOURCES:
        fetch_source(src, data_dir, quiet=quiet)
    report = verify(data_dir)
    manifest = {
        "sources": {s.key: asdict(s) for s in SOURCES},
        "state": report,
    }
    (data_dir / "provenance.json").write_text(json.dumps(manifest, indent=2))
    return report


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    p.add_argument("--check", action="store_true", help="report status, download nothing")
    args = p.parse_args(argv)

    if args.check:
        report = verify(args.data_dir)
    else:
        print(f"data dir: {args.data_dir}")
        report = ensure(args.data_dir)

    ok = True
    for key, st in report.items():
        commit = (st["commit"] or "missing")[:12]
        print(f"\n{key}  @ {commit}   {'OK' if st['ok'] else 'INCOMPLETE'}")
        for rel, size in st["files"].items():
            shown = f"{size/1e6:.1f} MB" if size else "MISSING"
            print(f"    {rel:64} {shown:>10}")
        ok &= st["ok"]

    if not ok:
        print("\nsome files are missing -- see above", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
