"""Turn the annotation table into a ladder of candidate anchoring bases.

Every categorical column of the FlyWire annotation table is a partition of the
neurons, and every partition is a candidate answer to "where should the Fisher
be anchored?".  This module materialises that ladder -- from the coarsest
(flow: 3 groups) to the finest biological grouping (cell type: ~8.8k) -- and
aligns each one to the dense neuron index so it can be handed straight to
:class:`clfly.lgcl.bases.Partition`.

Two design points that matter for the science:

**Missing annotations get their own group.** A neuron with no recorded cell type
is not "part of group 0"; each unannotated neuron becomes a singleton group of
its own.  That keeps the partition a genuine partition of every neuron (so the
projection is well defined) without pretending we know something we do not --
and it does not inflate the biological basis's apparent power, because singleton
groups add free parameters, which is exactly what the matched-budget accounting
in :mod:`clfly.lgcl.bases` charges for.

**Coverage is reported, not hidden.** A basis built on 12% of neurons is a
different object from one built on 99%, and the number should be in the results
table.

The ladder matters because granularity trades off: 3 groups barely constrain the
covariance (nearly the full matrix, no compression, no benefit), while 8,800
groups approach the diagonal's opposite extreme.  There should be a sweet spot,
and the question is where the *biological* groupings put it relative to
size-matched random partitions.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .graph import ANNOTATION_FILE, DEFAULT_DATA_DIR

# Coarse -> fine.  Names are the actual column names in the annotation table.
# `hemibrain_type` is dropped: it is defined only for the hemibrain subset and
# would mostly measure "is this neuron in the hemibrain".
BASIS_LADDER: tuple[str, ...] = (
    "flow",
    "super_class",
    "cell_class",
    "cell_sub_class",
    "supertype",
    "ito_lee_hemilineage",
    "hartenstein_hemilineage",
    "cell_type",
    "nerve",
    "side",
)

# Columns that are identifiers rather than groupings; never used as a basis.
NOT_A_BASIS = frozenset(
    {"root_id", "supervoxel_id", "nucleus_id", "vfb_id", "fbbt_id",
     "pos_x", "pos_y", "pos_z", "soma_x", "soma_y", "soma_z",
     "top_nt", "known_nt", "top_nt_conf", "known_nt_source",
     "status", "dimorphism", "matching_notes", "fru_dsx", "synonyms",
     "hemibrain_type"}
)


@dataclass
class Annotations:
    """The annotation table, indexed by ``root_id``."""

    frame: pd.DataFrame

    @property
    def n_rows(self) -> int:
        return len(self.frame)

    def available_bases(self) -> list[str]:
        """Categorical columns usable as a partition, coarse to fine."""
        out = [c for c in BASIS_LADDER if c in self.frame.columns]
        extra = [c for c in self.frame.columns
                 if c not in out and c not in NOT_A_BASIS
                 and self.frame[c].dtype == object]
        out.extend(sorted(extra))
        return out

    def labels_and_names(self, column: str, root_ids: np.ndarray,
                         missing: str = "singleton"):
        """Like :meth:`labels`, but also return the group *name* for each label id.

        Used wherever a downstream step has to reason about what a group means
        rather than just that it is a group -- matching an assembly by cell-type
        prefix, or writing a human-readable group table.
        """
        vals = self.frame[column].reindex(root_ids).to_numpy(dtype=object)
        present = ~np.asarray(pd.isna(vals))
        named_codes, uniques = pd.factorize(vals[present])
        names = [str(u) for u in uniques]
        n_named = len(names)

        if missing == "drop":
            out = np.full(len(vals), -1, dtype=np.int64)
            out[present] = named_codes
            return out, names

        out = np.empty(len(vals), dtype=np.int64)
        out[present] = named_codes
        miss = np.flatnonzero(~present)
        if missing == "shared":
            out[miss] = n_named
            names = names + [f"__missing__"]
        elif missing == "singleton":
            out[miss] = np.arange(n_named, n_named + len(miss))
            names = names + [f"__missing__:{i}" for i in miss]
        else:
            raise ValueError(f"unknown missing policy {missing!r}")
        return out, names

    def labels(self, column: str, root_ids: np.ndarray,
               missing: str = "singleton") -> np.ndarray:
        """Partition labels aligned to the dense neuron index.

        ``missing`` decides what happens to neurons with no value in ``column``:

        ``"singleton"`` (default) — each gets a private group.  The partition
            stays a genuine partition of every neuron, and no structure is
            invented.  The cost is that a column with poor coverage degenerates
            toward the diagonal (a near-singleton partition keeps only the
            diagonal, i.e. it *becomes* EWC), which the basis table reports.
        ``"shared"`` — all unannotated neurons pool into one group.  Keeps the
            parameter count low, but asserts within-group covariance across
            neurons that have nothing in common.  Useful only as a robustness
            check against the singleton reading.
        ``"drop"`` — restrict to annotated neurons; labels index only those.
            Use with :meth:`annotated_mask`.

        Returns integer labels in ``0..n_groups-1`` over the full index (or over
        the annotated subset for ``"drop"``).
        """
        return self.labels_and_names(column, root_ids, missing=missing)[0]

    def annotated_mask(self, column: str, root_ids: np.ndarray) -> np.ndarray:
        """Boolean mask of neurons that actually carry a value in ``column``."""
        vals = self.frame[column].reindex(root_ids).to_numpy(dtype=object)
        return ~np.asarray(pd.isna(vals))

    def coverage(self, column: str, root_ids: np.ndarray) -> float:
        return float(self.annotated_mask(column, root_ids).mean())


def load_annotations(data_dir: Path = DEFAULT_DATA_DIR) -> Annotations:
    """Read the per-neuron annotation table and key it by ``root_id``."""
    path = Path(data_dir) / ANNOTATION_FILE
    df = pd.read_csv(path, sep="\t", low_memory=False)
    if "root_id" not in df.columns:
        raise ValueError(f"{path} has no root_id column; got {list(df.columns)[:8]}")
    df = df.drop_duplicates(subset="root_id").set_index("root_id", drop=False)
    return Annotations(frame=df)


def basis_table(ann: Annotations, root_ids: np.ndarray,
                missing: str = "singleton") -> pd.DataFrame:
    """One row per candidate basis: granularity, coverage, and how much it constrains.

    This is the benchmark card for the basis ladder -- the numbers a reader needs
    to judge whether a comparison between bases is meaningful at all.

    The column that decides everything is ``constrained_fraction``, the share of
    the covariance the projection actually zeroes.  It exposes the trap in this
    ladder: very fine partitions (``nerve``, ``supertype``) are near-singleton,
    and a near-singleton partition keeps only the diagonal -- so the "finest
    biological basis" quietly *is* plain EWC.  Coarse partitions at the other end
    keep nearly everything and constrain nothing.  Only the middle has room for a
    basis to matter, which is why every comparison downstream must be matched on
    this number rather than on group count.
    """
    n = len(root_ids)
    total_entries = n * (n + 1) // 2
    rows = []
    for col in ann.available_bases():
        lab = ann.labels(col, root_ids, missing=missing)
        named = lab[lab >= 0]
        sizes = np.bincount(lab[lab >= 0]) if len(named) else np.zeros(0, dtype=int)
        n_params = int(np.sum(sizes * (sizes + 1) // 2)) if len(sizes) else 0
        rows.append({
            "basis": col,
            "named_groups": int(len(sizes)),
            "coverage": ann.coverage(col, root_ids),
            "largest_group": int(sizes.max()) if len(sizes) else 0,
            "median_group": float(np.median(sizes)) if len(sizes) else 0.0,
            "n_parameters": n_params,
            "constrained_fraction": 1.0 - n_params / total_entries,
        })
    return (pd.DataFrame(rows)
            .sort_values("constrained_fraction")
            .reset_index(drop=True))


def ladder(ann: Annotations, root_ids: np.ndarray, names=None) -> dict[str, np.ndarray]:
    """``name -> labels`` for each requested basis (default: the whole ladder)."""
    names = names or ann.available_bases()
    return {n: ann.labels(n, root_ids) for n in names}
