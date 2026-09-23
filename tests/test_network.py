"""Tests for the connectome-constrained rate network.

The torch suite is marked so it skips cleanly when torch is absent — the network is an
optional extra in ``pyproject.toml``, and the rest of the project must stay runnable
without it.
"""

from __future__ import annotations

import os

import numpy as np
import pytest

from clfly.connectome import graph
from clfly.connectome.tasks import overlap_controlled_supports
from clfly.network import tasks as rate_tasks
from clfly.network.model import RateConfig, build_net

torch = pytest.importorskip("torch", reason="torch is an optional extra")


@pytest.fixture(scope="module")
def small_circuit():
    """A synthetic circuit: no downloaded data needed."""
    import scipy.sparse as sp
    rng = np.random.default_rng(0)
    n = 40
    A = sp.csr_matrix((rng.random((n, n)) < 0.15) * rng.normal(size=(n, n)))
    conn = graph.Connectome(n_neurons=n, root_ids=np.arange(n), W=A)

    from clfly.connectome.circuits import Circuit
    labels = {"cell_class": np.repeat(np.arange(4), n // 4)}
    names = {f"grp{i}": [f"C{k}" for k in range(4)] for i in [0]}
    return Circuit(name="synthetic", net=conn, labels=labels,
                   value_names={"cell_class": names["grp0"]})


# --------------------------------------------------------------------------
# the mask and the initialisation
# --------------------------------------------------------------------------
def test_build_net_preserves_the_connectome_support_and_strengths(small_circuit):
    net = build_net(small_circuit)
    W = small_circuit.net.weights()
    assert net.n_params == W.nnz
    assert net.mask.shape == (small_circuit.n_neurons,) * 2
    np.testing.assert_array_equal(net.mask.nonzero()[0], W.tocoo().row)
    np.testing.assert_array_equal(net.mask.nonzero()[1], W.tocoo().col)
    np.testing.assert_allclose(net.w0, W.data)
    # the sign pattern is the connectome's, not learned away at init
    assert (np.sign(net.w0) == np.sign(W.data)).all()


def test_recurrent_matrix_matches_the_masked_weights(small_circuit):
    net = build_net(small_circuit)
    mod = net.torch_model()
    with torch.no_grad():
        mod.theta.copy_(torch.from_numpy(net.w0).float())
        W = mod.recurrent()
    expected = small_circuit.net.weights().toarray()
    np.testing.assert_allclose(W.numpy(), expected, atol=1e-5)
    # and it is genuinely sparse: no weight outside the connectome's support
    assert int((W.numpy() == 0).sum()) > 0.5 * expected.size


def test_forward_shape_and_finiteness(small_circuit):
    net = build_net(small_circuit, RateConfig(tau=6))
    mod = net.torch_model()
    u = torch.zeros(3, 6, small_circuit.n_neurons)
    u[:, :, :5] = 1.0
    traj = mod(u)
    assert traj.shape == (3, 6, small_circuit.n_neurons)
    assert torch.isfinite(traj).all()


def test_zero_input_gives_a_decaying_zero_state(small_circuit):
    """With no drive and a zero bias the state must stay at zero."""
    net = build_net(small_circuit, RateConfig(tau=5))
    mod = net.torch_model()
    traj = mod(torch.zeros(2, 5, small_circuit.n_neurons))
    assert torch.allclose(traj, torch.zeros_like(traj))


def test_it_can_actually_learn(small_circuit):
    """A model that cannot reduce its own training loss makes the benchmark vacuous."""
    task = rate_tasks.make_task(
        small_circuit, "toy", ("cell_class", ("C0",)), ("cell_class", ("C1",)),
        n_classes=3, n_train=48, n_test=24, tau=6, cap=10, seed=0)
    net = build_net(small_circuit, RateConfig(tau=6))
    mod = net.torch_model()
    head = torch.nn.Linear(task.n_readout, task.n_classes)
    opt = torch.optim.Adam([mod.theta, mod.bias] + list(head.parameters()), lr=1e-2)
    U = torch.from_numpy(task.u_train).float()
    Y = torch.from_numpy(task.y_train).long()
    lossf = torch.nn.CrossEntropyLoss()

    def loss_now():
        traj = mod(U)
        return lossf(head(traj[:, -1, :][:, task.readout_neurons]), Y)

    before = float(loss_now().detach())
    for _ in range(150):
        opt.zero_grad()
        loss_now().backward()
        opt.step()
    after = float(loss_now().detach())
    assert after < before - 0.1, f"no learning: {before:.3f} -> {after:.3f}"


# --------------------------------------------------------------------------
# the task suite
# --------------------------------------------------------------------------
def test_make_task_confines_the_stimulus_to_the_input_population(small_circuit):
    task = rate_tasks.make_task(
        small_circuit, "toy", ("cell_class", ("C0",)), ("cell_class", ("C2",)),
        n_classes=3, n_train=16, n_test=8, tau=4, cap=5, seed=0)
    assert task.u_train.shape == (16, 4, small_circuit.n_neurons)
    non_input = np.setdiff1d(np.arange(small_circuit.n_neurons), task.input_neurons)
    assert np.all(task.u_train[:, :, non_input] == 0.0)
    assert task.u_train[:, :, task.input_neurons].std() > 0
    # the read-out population is disjoint from the input one here, as in the real suite
    assert len(np.intersect1d(task.input_neurons, task.readout_neurons)) == 0


def test_overlap_controlled_supports_hits_the_target_exactly():
    rng = np.random.default_rng(0)
    for overlap in (0.0, 0.25, 0.5, 1.0):
        supports = overlap_controlled_supports(500, 5, 40, overlap, rng)
        assert all(len(s) == 40 for s in supports)
        expected = int(round(overlap * 40))
        for j in range(5):
            for k in range(j + 1, 5):
                assert len(np.intersect1d(supports[j], supports[k])) == expected


def test_overlap_controlled_supports_rejects_impossible_requests():
    with pytest.raises(ValueError):
        overlap_controlled_supports(50, 10, 40, 0.0,
                                               np.random.default_rng(0))
    with pytest.raises(ValueError):
        overlap_controlled_supports(500, 5, 40, 1.5,
                                               np.random.default_rng(0))


def test_environment_records_what_the_numbers_were_measured_in():
    """Rule 21's standing complaint, made checkable: the artifact says which environment produced it.

    A missing artifact cannot be restored across an environment (rule 21) and a difference between two runs
    of one configuration cannot be attributed to one — and this session spent a 58-minute
    `OMP_NUM_THREADS=1` sweep to rule the thread count out. `environment()` is what makes that free from here
    on, so the test pins the fields a reader needs rather than the exact values.
    """
    from experiments.e8_rate_network import environment

    env = environment()
    for key in ("omp_num_threads", "mkl_num_threads", "torch_num_threads",
                "torch_num_interop_threads", "torch_version", "python", "platform"):
        assert key in env, f"environment() must record {key}"
    assert isinstance(env["torch_num_threads"], int)
    assert isinstance(env["torch_num_interop_threads"], int)
    # "unset" is a *value*, not a missing key: most artifacts in this repo were produced with no OMP variable
    # set at all, and a reader who cannot tell "unset" from "not recorded" has learned nothing.
    assert env["omp_num_threads"] == os.environ.get("OMP_NUM_THREADS", "unset")


def test_the_artifact_payload_includes_the_environment():
    """The wiring, not just the function: an `environment()` nobody calls records nothing."""
    import inspect

    from experiments import e8_rate_network

    src = inspect.getsource(e8_rate_network.main)
    assert '"environment": environment()' in src


def test_relative_drift_is_scale_free_and_zero_for_a_body_that_does_not_move():
    """The quantity the network line has never recorded: how far the recurrent body moved.

    Every claim in the paper is about accuracy, and forgetting has to come from the weights. A frozen body is
    the case that makes the measurement checkable -- it cannot move, so its drift must be exactly zero, and
    that is also the control for the instrument itself.
    """
    import numpy as np

    from experiments.e8_rate_network import relative_drift

    theta = np.array([1.0, -2.0, 3.0, 0.5])
    assert relative_drift(theta, theta.copy()) == 0.0          # a frozen body
    assert relative_drift(theta, 2.0 * theta) == 1.0           # relative, not absolute
    assert relative_drift(theta, theta + np.array([1.0, 0, 0, 0])) == pytest.approx(
        1.0 / np.linalg.norm(theta))


def test_first_order_damage_reports_its_two_factors_separately():
    """`<grad, displacement>` and the magnitudes it is the product of.

    e107 showed the two candidate explanations of network forgetting -- how far the body moved, and how much
    the task needed it -- are both monotone in the read-out and neither orders the forgetting. So a first-order
    term that does order it could be doing so through either factor, and the factors are stored beside the
    product rather than folded into it.
    """
    import numpy as np

    from experiments.e8_rate_network import first_order_damage

    g = np.array([1.0, 0.0, 0.0])
    parallel = first_order_damage(g, np.array([2.0, 0.0, 0.0]))
    assert parallel["first_order"] == 2.0
    assert parallel["cosine"] == 1.0
    assert parallel["disp_norm"] == 2.0

    orthogonal = first_order_damage(g, np.array([0.0, 3.0, 0.0]))
    assert orthogonal["first_order"] == 0.0
    assert orthogonal["cosine"] == 0.0

    # A body that does not move must give a term of exactly zero with a defined cosine, not a nan: the frozen
    # control is what validates the instrument and a 0/0 there would make it unreadable.
    frozen = first_order_damage(g, np.zeros(3))
    assert frozen["first_order"] == 0.0
    assert frozen["cosine"] == 0.0
    assert frozen["disp_norm"] == 0.0
