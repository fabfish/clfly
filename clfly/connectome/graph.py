"""The FlyWire v783 graph: a fixed sparse wiring diagram.

This is the substrate. A synapse-level edge list becomes a signed sparse
adjacency matrix over 138k neurons, with the wiring frozen and the weights
available to be learned.  Everything downstream -- task circuits, candidate
anchoring bases, rewiring controls -- is a view onto this object.

The neuron *index* (0-based, dense) is the coordinate system.  ``root_id`` is the
FlyWire identifier and is what annotation tables key on; the two are kept side by
side so joins stay honest.

Data is read from ``data/`` (see :mod:`clfly.connectome.fetch`) and never
committed -- FlyWire is CC BY-NC.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = REPO_ROOT / "data"

CONNECTIVITY_FILE = "drosophila_brain_model/Connectivity_783.parquet"
COMPLETENESS_FILE = "drosophila_brain_model/Completeness_783.csv"
ANNOTATION_FILE = "flywire_annotations/supplemental_files/Supplemental_file1_neuron_annotations.tsv"

# Synapse counts span four orders of magnitude (1 .. ~1900).  A linear weight
# would let a handful of giant synapses dominate every gradient, so the default
# is the log compression the connectome-modelling literature converged on.
WEIGHT_SCALE = "log1p"


@dataclass
class Connectome:
    """A dense-indexed, signed, sparse wiring diagram.

    Attributes
    ----------
    n_neurons : number of indexed neurons (the whole v783 set, often larger than
        the number that actually appear in the edge list).
    root_ids : ``(n_neurons,)`` FlyWire root id for each dense index.
    W : ``(n_neurons, n_neurons)`` CSR, signed synapse counts, ``W[i, j]`` is
        the number of synapses from ``i`` to ``j`` (negative when inhibitory).
    """

    n_neurons: int
    root_ids: np.ndarray
    W: sp.csr_matrix

    # -- basic shape queries ------------------------------------------------
    @property
    def n_edges(self) -> int:
        return int(self.W.nnz)

    @property
    def density(self) -> float:
        n = self.n_neurons
        return self.n_edges / (n * (n - 1)) if n > 1 else 0.0

    def out_degree(self) -> np.ndarray:
        return np.diff(self.W.indptr).astype(np.int64)

    def in_degree(self) -> np.ndarray:
        return np.diff(self.W.tocsc().indptr).astype(np.int64)

    def active(self) -> np.ndarray:
        """Indices of neurons that appear in the edge list at all."""
        return np.flatnonzero((self.out_degree() + self.in_degree()) > 0)

    # -- weights ------------------------------------------------------------
    def weights(self, scale: str = WEIGHT_SCALE) -> sp.csr_matrix:
        """Synapse counts mapped to real-valued synaptic weights.

        ``log1p`` (default) compresses the heavy tail while keeping sign;
        ``sign`` gives unit weights (pure topology); ``raw`` gives counts.
        """
        W = self.W.copy()
        if scale == "raw":
            return W
        data = W.data
        if scale == "log1p":
            W.data = np.sign(data) * np.log1p(np.abs(data))
        elif scale == "sign":
            W.data = np.sign(data)
        else:
            raise ValueError(f"unknown weight scale {scale!r}")
        return W

    def excitatory_mask(self) -> tuple[sp.csr_matrix, sp.csr_matrix]:
        """Split into ``(E, I)`` with non-negative weights each."""
        W = self.W
        pos = W.copy()
        pos.data = np.clip(pos.data, 0, None)
        neg = W.copy()
        neg.data = -np.clip(neg.data, None, 0)
        return pos, neg

    # -- structure ----------------------------------------------------------
    def stats(self) -> dict:
        od, idg = self.out_degree(), self.in_degree()
        act = self.active()
        return {
            "n_neurons": self.n_neurons,
            "n_edges": self.n_edges,
            "n_active": int(len(act)),
            "density": self.density,
            "synapses_total": int(np.abs(self.W.data).sum()),
            "out_degree_mean": float(od[act].mean()) if len(act) else 0.0,
            "out_degree_max": int(od.max()) if self.n_neurons else 0,
            "in_degree_max": int(idg.max()) if self.n_neurons else 0,
            "inhibitory_fraction": float((self.W.data < 0).mean()) if self.n_edges else 0.0,
        }

    def largest_eigenvalues(self, k: int = 10) -> np.ndarray:
        """Top ``k`` eigenvalues of the symmetrised weight matrix.

        The spectrum is the cheapest summary of "is this random or structured"
        that we have, and it is the thing LGCL's finding 1 is about: a random
        rotation flattens it, a real connectome does not.
        """
        A = self.weights()
        S = ((A + A.T) * 0.5).astype(np.float64)
        k = min(k, self.n_neurons - 2)
        if k <= 0:
            return np.zeros(0)
        from scipy.sparse.linalg import eigsh
        try:
            w = eigsh(S, k=k, which="LA", return_eigenvectors=False, maxiter=5000)
        except Exception:  # pragma: no cover - ARPACK can fail to converge
            w = np.linalg.eigvalsh(S.toarray())[-k:]
        return np.sort(w)[::-1]

    # -- views --------------------------------------------------------------
    def subgraph(self, nodes: np.ndarray) -> "Connectome":
        """Induced subgraph on ``nodes``, re-indexed to ``0..len(nodes)-1``.

        Re-indexing rather than masking is deliberate: the exact LGCL machinery
        needs a ``d x d`` covariance, so the working dimension has to come down
        to a few thousand.  A circuit-level subgraph is the honest way to do that
        -- it keeps real wiring and real annotations at a tractable size.  The
        new ``root_ids`` are carried along, so annotation joins still work.
        """
        nodes = np.asarray(nodes, dtype=np.int64)
        if nodes.ndim != 1:
            raise ValueError("nodes must be a 1-D index array")
        if len(np.unique(nodes)) != len(nodes):
            raise ValueError("nodes contains duplicates")
        return Connectome(
            n_neurons=len(nodes),
            root_ids=self.root_ids[nodes],
            W=self.W[nodes][:, nodes].tocsr(),
        )

    def largest_component(self) -> "Connectome":
        """The weakly connected component holding the most neurons."""
        from scipy.sparse.csgraph import connected_components
        n_comp, labels = connected_components(self.W, directed=True, connection="weak")
        if n_comp <= 1:
            return self
        counts = np.bincount(labels)
        return self.subgraph(np.flatnonzero(labels == counts.argmax()))


# --------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------
def load_root_ids(data_dir: Path = DEFAULT_DATA_DIR) -> np.ndarray:
    """The ``(n_neurons,)`` root-id vector defining the dense index.

    The completeness list is the authoritative v783 neuron list, and its row
    order is what defines the dense indexing used throughout the package.

    Detection is by value, not by name: the shipped CSV's columns are
    ``Unnamed: 0`` (the FlyWire root id, ~7.2e17) and ``Completed`` (a boolean
    flag).  Picking the wrong one yields an all-``True`` "id" vector that joins
    to nothing -- which is exactly the bug this function now refuses to make.
    """
    path = Path(data_dir) / COMPLETENESS_FILE
    df = pd.read_csv(path)

    named = [c for c in df.columns if c.strip().lower().replace(" ", "_")
             in ("root_id", "rootid", "id", "bodyid", "body_id")]
    if named:
        return df[named[0]].to_numpy()

    id_like = [c for c in df.columns
               if pd.api.types.is_integer_dtype(df[c]) and df[c].abs().max() > 1e12]
    if not id_like:
        raise ValueError(
            f"no root-id-like column in {path.name}; columns are {list(df.columns)}. "
            "Refusing to guess -- an all-boolean 'id' column joins to nothing."
        )
    return df[id_like[0]].to_numpy()


def build(
    data_dir: Path = DEFAULT_DATA_DIR,
    min_synapses: int = 1,
    signed: bool = True,
    verbose: bool = False,
) -> Connectome:
    """Load the edge list and assemble a :class:`Connectome`.

    Synapses between the same ordered pair are summed, which is what turns the
    15M-row synapse table into the ~3.7M-connection wiring diagram.

    ``min_synapses > 1`` drops weak connections -- useful for the sparsification
    controls, and for keeping the learnable parameter count tractable.
    """
    data_dir = Path(data_dir)
    root_ids = load_root_ids(data_dir)
    n = len(root_ids)

    df = pd.read_parquet(
        data_dir / CONNECTIVITY_FILE,
        columns=["Presynaptic_ID", "Postsynaptic_ID", "Presynaptic_Index",
                 "Postsynaptic_Index", "Connectivity", "Excitatory"],
    )
    if verbose:
        print(f"  synapse rows: {len(df):,}")

    pre = df["Presynaptic_Index"].to_numpy(np.int64)
    post = df["Postsynaptic_Index"].to_numpy(np.int64)
    counts = df["Connectivity"].to_numpy(np.int64)
    sign = df["Excitatory"].to_numpy(np.int64)

    # The shipped table keeps magnitude and sign in separate columns:
    # `Connectivity` is the (unsigned) synapse count and `Excitatory` is +-1.
    # The signed weight is their product.  Assert both facts rather than
    # assuming them -- silently taking the unsigned column would make every
    # inhibitory synapse look excitatory, and nothing downstream would notice.
    if counts.min() < 0:
        raise ValueError("expected Connectivity to be an unsigned count")
    if not set(np.unique(sign)).issubset({-1, 1}):
        raise ValueError(f"expected Excitatory in {{-1, 1}}, got {np.unique(sign)}")
    syn = (sign * counts).astype(np.float64)

    # Verify that the file's own indices really are positions in the
    # completeness list.  If they were a private enumeration instead, every
    # join to annotations and every partition label would be silently permuted
    # -- a failure that produces plausible-looking numbers and no error.
    _verify_index_alignment(df, root_ids, verbose=verbose)

    if pre.max() >= n or post.max() >= n:
        raise ValueError(
            f"index out of range: max pre={pre.max()}, post={post.max()}, n={n}"
        )

    W = sp.coo_matrix((syn, (pre, post)), shape=(n, n)).tocsr()
    W.sum_duplicates()

    if min_synapses > 1:
        W.data[np.abs(W.data) < min_synapses] = 0
        W.eliminate_zeros()

    if not signed:
        W.data = np.abs(W.data)

    if verbose:
        print(f"  edges after summing: {W.nnz:,}")
    return Connectome(n_neurons=n, root_ids=root_ids, W=W)


def _verify_index_alignment(df, root_ids: np.ndarray, sample: int = 200_000,
                            verbose: bool = False) -> None:
    """Check ``root_ids[index] == ID`` on a sample of edge rows.

    Raises if the mapping is broken, rather than letting a permutation through.
    """
    n = len(root_ids)
    sub = df.iloc[:: max(1, len(df) // sample)]
    for idx_col, id_col in (("Presynaptic_Index", "Presynaptic_ID"),
                            ("Postsynaptic_Index", "Postsynaptic_ID")):
        idx = sub[idx_col].to_numpy(np.int64)
        ids = sub[id_col].to_numpy(np.int64)
        ok = idx < n
        if not ok.all():
            raise ValueError(f"{idx_col} exceeds the neuron list ({n})")
        mismatch = np.count_nonzero(root_ids[idx] != ids)
        if mismatch:
            raise ValueError(
                f"{idx_col} is not an index into the completeness list: "
                f"{mismatch}/{len(idx)} sampled rows disagree. The edge table "
                "uses its own enumeration; build the id<->index map from the "
                "edge table itself before joining annotations."
            )
    if verbose:
        print("  index alignment verified against the completeness list")


# --------------------------------------------------------------------------
# partitions and modularity
# --------------------------------------------------------------------------
def modularity(W: sp.spmatrix, labels: np.ndarray) -> float:
    """Newman modularity ``Q`` of a node partition under undirected weights.

    ``Q`` measures how much more weight falls inside groups than chance would
    predict.  Used to check that a biological partition really does cut the
    connectome at its joints -- if cell types have no higher ``Q`` than a random
    partition of the same sizes, there is no structure for a basis to exploit.
    """
    A = ((W + W.T) * 0.5).tocsr()
    A.data = np.abs(A.data)
    m2 = A.sum()
    if m2 <= 0:
        return 0.0
    k = np.asarray(A.sum(axis=1)).ravel()
    _, g = np.unique(labels, return_inverse=True)
    G = g.max() + 1 if len(g) else 0
    if G <= 1:
        return 0.0
    Acoo = A.tocoo()
    inside = np.zeros(G)
    np.add.at(inside, g[Acoo.row], Acoo.data * (g[Acoo.row] == g[Acoo.col]))
    deg = np.zeros(G)
    np.add.at(deg, g, k)
    return float((inside - deg**2 / m2).sum() / m2)


def node_weights_on(W: sp.spmatrix, nodes: np.ndarray) -> np.ndarray:
    """Total synaptic weight incident to each node, restricted to a mask."""
    A = np.abs(W).tocsr()
    tot = np.asarray(A.sum(axis=1)).ravel() + np.asarray(A.sum(axis=0)).ravel()
    return tot[nodes]
