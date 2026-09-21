"""Circuit extraction: pick a tractable, well-annotated piece of the brain.

Why this is necessary rather than a convenience: the exact LGCL machinery needs a
``d x d`` covariance, and the whole brain is ``d = 138,113`` -- a single
dense matrix would be 152 GB.  The working dimension has to come down to a few
thousand, and the honest way to do that is to take a *circuit*: real neurons,
real wiring, real annotations, just fewer of them.

The selection is driven by the annotation vocabulary rather than by hand-picked
ids, so it is reproducible and auditable:

``super_class``  optic 77k / central 32k / sensory 17k / visual_projection 8k / ...
``cell_class``   ME>LO 22k / ME 19k / visual 11k / **Kenyon_Cell 5.2k** /
                 **CX 2.9k** / olfactory 2.3k / **ALPN 685** / **ALLN 429** /
                 **LHLN 514** / **DAN 331** / MBON / MBIN / ...
``cell_type``    10,331 groups, 98.9% coverage

The learning and navigation circuits -- mushroom body and central complex -- are
the natural target: they are the fly's canonical memory and heading systems, they
are densely annotated, and their cell classes give a genuine biological partition
to anchor in.  Two hundred thousand neurons of optic lobe would swamp the
statistics without adding anything to the question.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import scipy.sparse as sp

from .annotate import Annotations
from .graph import Connectome


@dataclass(frozen=True)
class SeedSpec:
    """A named way of selecting neurons by annotation value."""

    name: str
    column: str
    values: tuple[str, ...]
    note: str = ""


#: The mushroom body: the fly's associative-learning circuit.
MB_SEEDS = SeedSpec(
    name="mb",
    column="cell_class",
    values=("Kenyon_Cell", "MBON", "MBIN", "DAN"),
    note="Kenyon cells (sparse odour code) + output/inhibitory/ dopaminergic neurons",
)

#: The central complex: heading, navigation, motor planning.
CX_SEEDS = SeedSpec(
    name="cx",
    column="cell_class",
    values=("CX", "FB", "EB", "PB", "NO", "LAL"),
    note="ring attractor / compass neurons",
)

#: Olfactory input side, upstream of the mushroom body.
AL_SEEDS = SeedSpec(
    name="al",
    column="cell_class",
    values=("ALPN", "ALLN", "ALIN", "ALON", "olfactory", "LHLN", "LHCENT"),
    note="antennal lobe projection / local / input-output neurons",
)

DEFAULT_SPECS = (MB_SEEDS, CX_SEEDS, AL_SEEDS)


@dataclass
class Circuit:
    """A sub-connectome plus, for each candidate basis, a label vector.

    ``labels[basis][i]`` is the group of neuron ``i`` **within the subcircuit**,
    recomputed after extraction so that a biological group absent from the
    selection does not linger as an empty group.
    """

    name: str
    net: Connectome
    labels: dict[str, np.ndarray] = field(default_factory=dict)
    value_names: dict[str, list[str]] = field(default_factory=dict)

    @property
    def n_neurons(self) -> int:
        return self.net.n_neurons

    def basis_names(self) -> list[str]:
        return sorted(self.labels)

    def neuron_names(self, column: str) -> list[str]:
        """Per-neuron group name for one basis column (``"Kenyon_Cell"``, ...)."""
        names = self.value_names[column]
        return [names[i] for i in self.labels[column]]

    def covariance_gb(self) -> float:
        """Memory one dense ``d x d`` float64 matrix would take, in GB."""
        return self.net.n_neurons ** 2 * 8 / 1e9


# --------------------------------------------------------------------------
def select(net_root_ids: np.ndarray, ann: Annotations, spec: SeedSpec) -> np.ndarray:
    """Indices of neurons whose ``spec.column`` value is in ``spec.values``."""
    labels = ann.labels(spec.column, net_root_ids, missing="drop")
    present = labels >= 0
    values = np.asarray(ann.frame[spec.column].reindex(net_root_ids).to_numpy(dtype=object)[present])
    wanted = np.isin(values, np.asarray(spec.values, dtype=object))
    return np.flatnonzero(present)[wanted]


def expand(conn: Connectome, nodes: np.ndarray, hops: int = 1,
           direction: str = "both") -> np.ndarray:
    """Grow a node set along the wiring, ``hops`` times, in the given direction.

    ``"out"`` follows axons (where these neurons project to), ``"in"`` follows
    dendrites (what drives them), ``"both"`` ignores direction.  This is the only
    principled way to get a circuit's *partners* without hand-picking ids.
    """
    nodes = np.asarray(nodes, dtype=np.int64)
    A = abs(conn.W).astype(bool).tocsr()
    if direction == "in":
        A = A.T.tocsr()
    elif direction == "both":
        A = (A + A.T).astype(bool).tocsr()
    elif direction != "out":
        raise ValueError(f"unknown direction {direction!r}")

    cur = np.zeros(conn.n_neurons, dtype=bool)
    cur[nodes] = True
    for _ in range(hops):
        nxt = np.asarray(A[cur].sum(axis=0)).ravel() > 0
        cur = cur | nxt
    return np.flatnonzero(cur)


def subsample_fraction(labels: np.ndarray, frac: float,
                       rng: np.random.Generator | None = None) -> np.ndarray:
    """Keep a random ``frac`` of each group, preserving group identity and shape.

    Scaling every group by the same factor preserves the partition's size
    *distribution* up to sampling noise, which is what the matched-budget
    controls and ``constrained_fraction`` depend on.  Every group keeps at least
    one member, so no cell type disappears (which would silently change the
    candidate bases between runs).

    This is the honest way to make a circuit tractable.  An earlier version of
    this function kept the highest-degree neurons globally, which pulled in
    thousands of well-connected but unannotated neurons and dissolved the
    biological partition into singletons -- the partition looked rich while
    measuring nothing.
    """
    if not 0.0 < frac <= 1.0:
        raise ValueError("frac must be in (0, 1]")
    rng = rng or np.random.default_rng(0)
    labels = np.asarray(labels)
    keep = np.zeros(len(labels), dtype=bool)
    for g in np.unique(labels):
        idx = np.flatnonzero(labels == g)
        n_keep = max(1, int(round(len(idx) * frac)))
        if n_keep >= len(idx):
            keep[idx] = True
        else:
            keep[rng.choice(idx, size=n_keep, replace=False)] = True
    return np.flatnonzero(keep)


def extract(
    conn: Connectome,
    ann: Annotations,
    specs=DEFAULT_SPECS,
    hops: int = 1,
    direction: str = "both",
    max_neurons: int | None = 6000,
    basis_columns: tuple[str, ...] | None = None,
    missing: str = "singleton",
    name: str | None = None,
    seed: int = 0,
) -> Circuit:
    """Build a tractable subcircuit from annotation seeds.

    If the selection exceeds ``max_neurons``, it is proportionally subsampled per
    group (see :func:`subsample_fraction`) -- a compute budget, not a scientific
    choice.  The budget is **soft**: every group keeps at least one member (so no
    cell type silently disappears between runs), which with hundreds of groups
    pushes the achieved total somewhat above the target.  The achieved size is
    recorded in the circuit name and must be reported with any result, since a
    subsampled circuit is a sample of the real one, not the real one.
    """
    specs = tuple(specs)
    seeds = np.unique(np.concatenate([select(conn.root_ids, ann, s) for s in specs]))
    if len(seeds) == 0:
        raise ValueError("no neurons matched any seed spec; check the annotation column values")

    nodes = expand(conn, seeds, hops=hops, direction=direction) if hops else seeds

    columns = basis_columns or tuple(
        c for c in ("flow", "super_class", "cell_class", "cell_type",
                    "ito_lee_hemilineage", "supertype", "side")
        if c in ann.frame.columns
    )

    sampled = False
    if max_neurons is not None and len(nodes) > max_neurons:
        # Subsample on the finest well-covered column so the scaling is applied
        # to the structure the study actually varies.
        anchor = "cell_type" if "cell_type" in columns else columns[0]
        groups = ann.labels(anchor, conn.root_ids[nodes], missing=missing)
        rng = np.random.default_rng(seed)
        keep = subsample_fraction(groups, max_neurons / len(nodes), rng)
        nodes = nodes[keep]
        sampled = True

    sub = conn.subgraph(nodes)

    labels, value_names = {}, {}
    for col in columns:
        raw, names = ann.labels_and_names(col, sub.root_ids, missing=missing)
        # Drop groups that vanished with the subcircuit and renumber densely, so
        # Partition() sees a contiguous label space and the names stay aligned.
        uniq, inverse = np.unique(raw, return_inverse=True)
        remap = -np.ones(int(uniq.max()) + 1, dtype=np.int64)
        remap[uniq] = np.arange(len(uniq))
        labels[col] = remap[inverse]
        value_names[col] = [names[i] for i in uniq]

    auto_name = name or "+".join(s.name for s in specs)
    if hops:
        auto_name += f"+{hops}hop"
    if sampled:
        auto_name += f"@n{len(nodes)}"
    return Circuit(name=auto_name, net=sub, labels=labels, value_names=value_names)


def circuit_report(circ: Circuit) -> dict:
    """Sizes, wiring density, and per-basis coverage inside the subcircuit."""
    report = {
        "circuit": circ.name,
        "n_neurons": circ.n_neurons,
        "n_edges": circ.net.n_edges,
        "dense_covariance_gb": round(circ.covariance_gb(), 3),
    }
    for basis, lab in sorted(circ.labels.items()):
        sizes = np.bincount(lab)
        report[f"{basis}.groups"] = len(sizes)
        report[f"{basis}.largest"] = int(sizes.max())
    return report
