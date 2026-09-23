"""The saved checkpoint must contain every parameter the forward pass reads.

`e122`'s first run computed the loss along a chord between two seeds' bodies and got endpoint values
**sixty times** the loss the benchmark had just recorded on the same body. The cause was not the geometry:
`--save-theta` wrote `theta` and the decoders but **not the recurrent bias**, and `train_task` optimises
`[model.theta, model.bias]` -- so every point on the chord, including both endpoints, was evaluated on top of a
zero bias that the benchmark never produces.

The regression test is the instrument's own control rather than a list of keys: reload a saved checkpoint into a
fresh module, recompute the loss the runner recorded at that checkpoint, and require equality. A parameter
missing from the checkpoint cannot survive that, because its absence moves the loss by a factor rather than a
percent. Checking a key list instead would pass the moment somebody adds a new trainable parameter and forgets
it in the same way.
"""

from __future__ import annotations

import numpy as np
import pytest

from clfly.connectome import graph
from clfly.network import tasks as rate_tasks
from clfly.network.model import RateConfig, build_net

torch = pytest.importorskip("torch", reason="torch is an optional extra")


@pytest.fixture(scope="module")
def synthetic_circuit():
    """A two-population synthetic circuit, so the test needs no downloaded connectome."""
    import scipy.sparse as sp

    from clfly.connectome.circuits import Circuit

    rng = np.random.default_rng(0)
    n = 40
    A = sp.csr_matrix((rng.random((n, n)) < 0.15) * rng.normal(size=(n, n)))
    conn = graph.Connectome(n_neurons=n, root_ids=np.arange(n), W=A)
    return Circuit(name="synthetic", net=conn,
                   labels={"cell_class": np.repeat(np.arange(4), n // 4)},
                   value_names={"cell_class": ["C0", "C1", "C2", "C3"]})


def _suite(circ, shared_head: bool):
    specs = (("A", ("cell_class", ("C0",)), ("cell_class", ("C1",))),
             ("B", ("cell_class", ("C2",)), ("cell_class", ("C3",))))
    return rate_tasks.make_suite(circ, specs=specs, shared_head=shared_head, n_train=32,
                                 n_test=16, noise=1.0, n_classes=3, tau=4, cap=10)


@pytest.mark.parametrize("shared_head", [True, False])
def test_a_reloaded_checkpoint_reproduces_the_loss_the_runner_recorded(synthetic_circuit, tmp_path,
                                                                      shared_head):
    from argparse import Namespace

    from experiments.e8_rate_network import full_split_loss, run_method

    suite = _suite(synthetic_circuit, shared_head)
    args = Namespace(iters=25, lr=3e-3, batch=16, lam=3e-3, fisher_batches=2,
                     normalise_fisher=True, replay_batch=8, frozen_body=False,
                     shared_head=shared_head, save_theta=tmp_path)
    result = run_method(build_net(synthetic_circuit, RateConfig(tau=4, seed=0)), suite, "naive", args, seed=0)

    T = len(suite)
    with np.load(tmp_path / "naive_seed0.npz") as npz:
        for k in range(T):
            # a fresh module and a fresh decoder: nothing is carried over from training
            model = build_net(synthetic_circuit, RateConfig(tau=4, seed=0)).torch_model()
            with torch.no_grad():
                model.theta.copy_(torch.from_numpy(npz[f"after_task_{k}"]).float())
                model.bias.copy_(torch.from_numpy(npz[f"bias_after_task_{k}"]).float())
            if shared_head:
                heads = [torch.nn.Linear(suite[0].n_readout, sum(t.n_classes for t in suite))]
            else:
                heads = [torch.nn.Linear(t.n_readout, t.n_classes) for t in suite]
            for i, h in enumerate(heads):
                for p in ("weight", "bias"):
                    getattr(h, p).data.copy_(
                        torch.from_numpy(npz[f"head_{i}_{p}_after_task_{k}"]).float())
            for j in range(k + 1):
                got = full_split_loss(model, heads[0] if shared_head else heads[j], suite[j],
                                      shared_head, "train")
                want = result["retention_loss"][k][j]
                assert got == pytest.approx(want, abs=1e-6), (
                    f"checkpoint after_task_{k}, task {j}: reloaded {got:.6f} against the runner's "
                    f"recorded {want:.6f} -- a saved parameter is missing from the checkpoint")


def test_the_endpoint_loss_moves_by_a_factor_when_the_bias_is_dropped(synthetic_circuit, tmp_path):
    """The failure mode, stated as a size, so that "we would have noticed" is a measurement.

    If dropping the bias moved the loss by a few percent the previous test would be a tolerance question rather
    than an equality. It moves it by a factor -- and **the factor is how far the body has walked from its
    zero-bias initialisation**, which is why it is 3x on this forty-neuron circuit at 400 iterations and 60x on
    the paper's configuration. A short run would make this test vacuous for a reason that has nothing to do with
    the checkpoint format, so the iteration count is part of the claim.
    """
    from argparse import Namespace

    from experiments.e8_rate_network import full_split_loss, run_method

    suite = _suite(synthetic_circuit, shared_head=True)
    args = Namespace(iters=400, lr=3e-3, batch=16, lam=3e-3, fisher_batches=2,
                     normalise_fisher=True, replay_batch=8, frozen_body=False,
                     shared_head=True, save_theta=tmp_path)
    result = run_method(build_net(synthetic_circuit, RateConfig(tau=4, seed=0)), suite, "naive", args, seed=0)

    with np.load(tmp_path / "naive_seed0.npz") as npz:
        model = build_net(synthetic_circuit, RateConfig(tau=4, seed=0)).torch_model()
        heads = [torch.nn.Linear(suite[0].n_readout, sum(t.n_classes for t in suite))]
        k = len(suite) - 1
        with torch.no_grad():
            model.theta.copy_(torch.from_numpy(npz[f"after_task_{k}"]).float())
            model.bias.copy_(torch.from_numpy(npz[f"bias_after_task_{k}"]).float())
            for i, h in enumerate(heads):
                for p in ("weight", "bias"):
                    getattr(h, p).data.copy_(
                        torch.from_numpy(npz[f"head_{i}_{p}_after_task_{k}"]).float())
            intact = full_split_loss(model, heads[0], suite[k], True, "train")
            model.bias.data.zero_()              # the bug: a body with its bias never saved
            dropped = full_split_loss(model, heads[0], suite[k], True, "train")
    assert intact == pytest.approx(result["retention_loss"][k][k], abs=1e-6)
    assert dropped > 2.0 * intact, (
        f"dropping the bias moved the loss only {intact:.5f} -> {dropped:.5f}; the control in e122 would not "
        f"have caught it, so this test's premise is wrong")
