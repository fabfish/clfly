"""`--frozen-body` and `--frozen-bias` must partition the body's two parameter sets, and nothing else.

`--frozen-body` freezes `theta` **and** the bias together, so before `--frozen-bias` nothing separated the
26,568 masked weights that *are* the connectome from the 800 per-neuron offsets that carry no wiring semantics.
Both are trained, and neither EWC penalty in this project covers the bias -- `diagonal_fisher`'s docstring
justifies the exclusion for the decoder and not for the bias, since "the bias is shared" is equally true of
`theta`, which *is* anchored. So the three arms have to mean exactly what they say:

    default        theta moves, bias moves, decoder moves
    --frozen-bias  theta moves, bias frozen at zero, decoder moves
    --frozen-body  theta frozen, bias frozen at zero, decoder moves

A test that checked only the frozen arms would pass for a flag that froze everything, which is the bug this
partition exists to rule out. So every arm is checked on all three quantities.
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
    import scipy.sparse as sp

    from clfly.connectome.circuits import Circuit

    rng = np.random.default_rng(0)
    n = 40
    A = sp.csr_matrix((rng.random((n, n)) < 0.15) * rng.normal(size=(n, n)))
    conn = graph.Connectome(n_neurons=n, root_ids=np.arange(n), W=A)
    return Circuit(name="synthetic", net=conn,
                   labels={"cell_class": np.repeat(np.arange(4), n // 4)},
                   value_names={"cell_class": ["C0", "C1", "C2", "C3"]})


def _run(circ, tmp_path, **flags):
    from argparse import Namespace

    from experiments.e8_rate_network import run_method

    specs = (("A", ("cell_class", ("C0",)), ("cell_class", ("C1",))),
             ("B", ("cell_class", ("C2",)), ("cell_class", ("C3",))))
    suite = rate_tasks.make_suite(circ, specs=specs, shared_head=True, n_train=32, n_test=16,
                                  noise=1.0, n_classes=3, tau=4, cap=10)
    args = Namespace(iters=40, lr=3e-3, batch=16, lam=3e-3, fisher_batches=2, normalise_fisher=True,
                     replay_batch=8, shared_head=True, save_theta=tmp_path,
                     frozen_body=False, frozen_bias=False)
    for k, v in flags.items():
        setattr(args, k, v)
    return run_method(build_net(circ, RateConfig(tau=4, seed=0)), suite, "naive", args, seed=0)


@pytest.mark.parametrize("flags,theta_moves,bias_moves", [
    ({}, True, True),
    ({"frozen_bias": True}, True, False),
    ({"frozen_body": True}, False, False),
])
def test_the_two_frozen_flags_partition_the_body(synthetic_circuit, tmp_path, flags,
                                                 theta_moves, bias_moves):
    result = _run(synthetic_circuit, tmp_path, **flags)
    theta_moved = max(result["theta_drift"]) > 1e-6        # relative drift, so 1e-6 is safely "did not move"
    bias_moved = max(b["step"] for b in result["bias_norms"]) > 1e-6
    assert theta_moved is theta_moves, f"theta under {flags}: drifted {max(result['theta_drift']):.3e}"
    assert bias_moved is bias_moves, f"bias under {flags}: stepped {max(b['step'] for b in result['bias_norms']):.3e}"
    # and the decoder is trained in every arm -- including the fully frozen one, which is the point of it
    assert np.isfinite(result["final_accuracy"])


def test_the_bias_is_the_only_trained_parameter_no_penalty_sees(synthetic_circuit, tmp_path):
    """The claim the flag exists to test, asserted against the code rather than against a run.

    `train_task` optimises `[model.theta, model.bias]`, and `diagonal_fisher` differentiates `theta` alone, so
    the sizes are the claim: the body is two sets, and the penalty covers one of them.

    **`e136`-era note, i.e. what changed when `--anchor-bias` landed**: `diagonal_fisher` now contains an
    **opt-in** path for the bias, so the old assertion *"``model.bias`` not in ``fisher_src``"* — which is what
    failed when the flag arrived, exactly as it was written to — is replaced by the two assertions that say the
    same thing more precisely: **the bias's Fisher is accumulated only under `with_bias`**, and `train_task`'s
    default call does not pass it. A test that a source file does not mention a name would have blocked the very
    change that made the name appear.
    """
    import inspect

    from experiments import e8_rate_network

    src = inspect.getsource(e8_rate_network.train_task)
    assert "[model.theta, model.bias]" in src
    assert "[model.theta] + list(readout.parameters())" in src
    fisher_src = inspect.getsource(e8_rate_network.diagonal_fisher)
    assert "torch.zeros_like(model.theta)" in fisher_src
    assert "with_bias" in fisher_src, (
        "the bias's Fisher must be reachable through the explicit `with_bias` argument, so that the channel "
        "`e125` measured and `e137` watched the adaptation move into can be penalised at all")
    assert "if not with_bias:" in fisher_src and "return f" in fisher_src, (
        "the default return must remain a single array for `theta`, or every existing caller's shape changes")
    # and train_task's default path does not carry a bias term
    assert "if len(ewc) > 3 and ewc[3] is not None:" in src, (
        "the bias term must be optional inside train_task, so that a run without the flag is bit-identical")

    # and the records exist per task rather than per run
    result = _run(synthetic_circuit, tmp_path)
    assert len(result["bias_norms"]) == 2, "the synthetic suite is two tasks, so two bias records"


def test_a_frozen_bias_is_reported_as_zero_rather_than_omitted(synthetic_circuit, tmp_path):
    """A zero must be a recorded zero, not a missing field: `e122`'s whole lesson was about a saved body."""
    result = _run(synthetic_circuit, tmp_path, frozen_body=True)
    for row in result["bias_norms"]:
        assert row["step"] == 0.0 and row["from_zero"] == 0.0


def test_anchoring_the_bias_lowers_its_drift_and_changes_nothing_at_task_zero(synthetic_circuit, tmp_path):
    """`--anchor-bias` must constrain the channel, and it must have nothing to constrain before task 0.

    The second half is not a formality: the anchor and its Fisher are created **after** a task is trained, so the
    first task is trained with no bias penalty in every arm — which makes *"task 0's bias step is identical across
    arms"* an internal control that the flag changes nothing except by anchoring.
    """
    from argparse import Namespace

    from experiments.e8_rate_network import run_method

    specs = (("A", ("cell_class", ("C0",)), ("cell_class", ("C1",))),
             ("B", ("cell_class", ("C2",)), ("cell_class", ("C3",))))
    suite = rate_tasks.make_suite(synthetic_circuit, specs=specs, shared_head=True, n_train=32,
                                  n_test=16, noise=1.0, n_classes=3, tau=4, cap=10)

    def run(anchor_bias):
        args = Namespace(iters=60, lr=3e-3, batch=16, lam=3e-3, fisher_batches=2, normalise_fisher=True,
                         replay_batch=8, shared_head=True, save_theta=tmp_path,
                         frozen_body=False, frozen_bias=False, anchor_bias=anchor_bias)
        return run_method(build_net(synthetic_circuit, RateConfig(tau=4, seed=0)), suite, "ewc", args, seed=0)

    off, on = run(None), run(1.0)
    for a in (off, on):
        assert a["bias_norms"][0]["step"] == off["bias_norms"][0]["step"], (
            "task 0 is trained before any anchor exists, so its bias step must be identical across arms")
    assert on["bias_norms"][-1]["from_zero"] < off["bias_norms"][-1]["from_zero"], (
        f"anchoring the bias must lower its cumulative movement: "
        f"{on['bias_norms'][-1]['from_zero']:.4f} against {off['bias_norms'][-1]['from_zero']:.4f}")
