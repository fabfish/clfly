"""A connectome-constrained rate network — the non-linear substrate.

Everything in this project so far has been measured on the linear-Gaussian reduction,
where the connectome sets the *problem geometry* exactly but the dynamics are a
linearisation around a fixed point.  That reduction bought the exact oracle, which is
why it was worth doing; but the paper's own limitations section says a rate-network
benchmark with behavioural tasks is the natural next instrument, and this is it.

**The model.** A discrete-time rate network with the connectome's wiring as a fixed
sparse mask:

    x_{t+1} = (1 - alpha) x_t + alpha * tanh( W x_t + W_in u_t + b )

where ``W = M * theta`` is elementwise-masked by the connectome (`M` is the binary
support pattern and `theta` the trainable weights), and ``u_t`` is the stimulus
delivered to a task's input population.  Because ``tanh`` is smooth this trains by
ordinary backprop-through-time; no surrogate gradients are needed.

**What is learnable, and why it matters for the basis question.**  Two parameterisation
levels are available and they are not equivalent:

``"weights"`` — one parameter per connectome synapse.  The natural *partition* of this
    parameter space is by cell type pair, which is what carries the project's basis
    question over to the network: a diagonal Fisher in the weight coordinate basis is
    the network's EWC, and a block-diagonal Fisher over (pre cell type, post cell type)
    is the network's version of the anchoring basis that won on the linear substrate.
``"gains"`` — one parameter per presynaptic neuron, scaling its whole outgoing
    projection (the parameterisation `flyvis` uses).  Far fewer parameters, and its
    coordinate basis is already the neuron basis, so the partition question does not
    arise.

The default is ``"weights"`` because it is the one that makes the basis question
meaningful.

**Scale.** The circuit has ~27k synapses over ~1300 neurons, so a forward pass is a
sparse matvec and BPTT over 20-30 steps is cheap on CPU.  The mask is kept as a sparse
tensor and the trainable weights as a dense vector over its support, so a Fisher
diagonal is a vector of the same length.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import scipy.sparse as sp

from ..connectome.circuits import Circuit
from ..connectome.graph import WEIGHT_SCALE


@dataclass
class RateConfig:
    """Architecture and training hyper-parameters."""

    alpha: float = 0.3          # leak; 1.0 is a pure tanh recurrence
    tau: int = 12               # timesteps per stimulus
    dt: float = 0.5
    input_scale: float = 1.0
    weight_scale: float | None = None   # None: use the connectome's log1p weights
    seed: int = 0


@dataclass
class ConnectomeNet:
    """The network plus its fixed mask and the connectome-derived initial weights.

    Deliberately holds numpy/sparse objects rather than torch tensors so the
    construction stays testable without torch; :meth:`torch_model` materialises the
    learnable module.
    """

    mask: sp.csr_matrix                     # (n, n) binary support
    w0: np.ndarray                          # (nnz,) connectome-derived init
    bias_dim: int
    config: RateConfig = field(default_factory=RateConfig)

    @property
    def n_neurons(self) -> int:
        return self.mask.shape[0]

    @property
    def n_params(self) -> int:
        return int(self.mask.nnz)

    def torch_model(self, device: str = "cpu"):
        """Materialise the learnable module.  Imports torch lazily."""
        return _materialise(self, device=device)


def build_net(circ: Circuit, config: RateConfig | None = None,
              scale: str = WEIGHT_SCALE) -> ConnectomeNet:
    """Wrap a circuit's connectivity as a fixed mask plus connectome initial weights.

    The mask is the connectome's own sign pattern (kept, not learned), and the
    initial weights are its ``log1p`` synapse strengths.  Preserving the sign matters:
    it is what makes the network a *connectome-constrained* model rather than an
    arbitrary sparse net, and it is the reason the inhibition/excitation balance of
    the real circuit is present at initialisation.
    """
    W = circ.net.weights(scale).tocsr().astype(np.float64)
    mask = (W != 0).astype(np.float64)
    return ConnectomeNet(mask=mask.tocsr(), w0=W.data.copy(),
                         bias_dim=circ.n_neurons,
                         config=config or RateConfig())


# --------------------------------------------------------------------------
# torch implementation
# --------------------------------------------------------------------------
def _make_module():
    import torch
    import torch.nn as nn

    class _RateNet(nn.Module):
        """``x_{t+1} = (1-a) x_t + a tanh(W x_t + W_in u_t + b)``, ``W`` masked."""

        def __init__(self, mask, w0, alpha, tau):
            super().__init__()
            n = mask.shape[0]
            self.register_buffer("mask_idx", torch.from_numpy(
                np.stack(mask.nonzero(), axis=1).astype(np.int64)))
            self.register_buffer("mask_shape", torch.tensor([n, n]))
            self.theta = nn.Parameter(torch.from_numpy(w0).float())
            self.bias = nn.Parameter(torch.zeros(n))
            self.alpha = float(alpha)
            self.tau = int(tau)

        def recurrent(self):
            idx = self.mask_idx
            W = torch.zeros(tuple(self.mask_shape), dtype=self.theta.dtype,
                            device=self.theta.device)
            W = W.index_put((idx[:, 0], idx[:, 1]), self.theta)
            return W

        def forward(self, u, w_in=None):
            """Run the recurrence.

            ``u`` is ``(batch, tau, n_neurons)`` when ``w_in`` is ``None`` — the
            stimulus already lives in neuron space, which is how this project delivers
            it, so there is no separate input pathway to absorb task-specific
            structure.  Passing ``w_in`` instead lets ``u`` be ``(batch, tau, n_in)``
            for a projected stimulus.
            """
            W = self.recurrent()
            x = torch.zeros(u.shape[0], self.mask_shape[0], device=u.device,
                            dtype=u.dtype)
            traj = []
            for t in range(self.tau):
                drive = x @ W.T + self.bias
                drive = drive + (u[:, t] @ w_in.T if w_in is not None else u[:, t])
                x = (1.0 - self.alpha) * x + self.alpha * torch.tanh(drive)
                traj.append(x)
            return torch.stack(traj, dim=1)     # (batch, tau, n)

    return _RateNet


def _materialise(net: ConnectomeNet, device: str = "cpu"):
    mod = _make_module()(net.mask, net.w0, net.config.alpha, net.config.tau)
    return mod.to(device)
