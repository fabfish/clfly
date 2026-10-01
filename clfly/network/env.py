"""A closed loop: the environment's next input is a function of the agent's own last output.

Every task builder in this repository writes a ``u`` array up front -- `make_task` and `make_sequence_task` both
return ``(n, tau, n_neurons)`` -- and the model consumes it, so the world can never see what the agent did. That is
what makes the suite **open-loop**, and it is the second of the two things `e322` named as ways to give the trial a
time axis: a writer whose value changes with the step, which `e323` built, and *an environment in the training
loop*, which is this module.

**The contract is one callable.** :meth:`CueActionEnv.feedback` returns ``fn(x, t) -> (batch, n)``, and
:meth:`~clfly.network.model.ConnectomeNet.torch_model`'s forward pass **adds** it to the step's input, where ``x``
is the state *before* that step's update. So the agent's own activity at step ``t - 1`` is part of its input at
step ``t``, and the loop is differentiable: backprop-through-time crosses it exactly as it crosses the recurrence.

**The world this builds is the smallest one that needs a loop.** The cue is shown at step ``0`` and then taken
away; from step ``1`` on, the only thing in the input is the agent's own last action, read off a set of its
neurons and shown back at another. So the trial is a **delayed report of a cue that is gone**, and the task's
information has to survive both the recurrence and the agent's own feedback -- which is the first setting in this
repository where the agent's output is an input to itself.

**What is deliberately not here.** There is no reward, no episode boundary and no policy: this module supplies the
*environment*, and a learning rule for acting in it is a separate question. The action is a smooth function of the
state (a ``tanh`` of the mean activity over the action neurons), so it can be differentiated through rather than
being a `sign` that cannot; a hard action is a one-word change and is named in the finding as a thing this unit
does not measure.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class CueActionEnv:
    """A one-cue, one-feedback-channel environment.

    ``cue_neurons`` carries a per-symbol pattern at step ``0``; ``action_neurons`` are the state neurons whose mean
    activity decides the agent's action; ``feedback_neurons`` carry that action back into the input from step ``1``
    on. The three sets are drawn disjoint so that a channel cannot silently be reading the other's neurons, and the
    draw is recorded for the same reason every other draw in this project is.
    """

    n_neurons: int
    tau: int
    cue_neurons: np.ndarray
    action_neurons: np.ndarray
    feedback_neurons: np.ndarray
    cue_templates: np.ndarray                 # (n_symbols, len(cue_neurons))
    scale: float = 1.0
    gain: float = 1.0

    @property
    def n_symbols(self) -> int:
        return int(self.cue_templates.shape[0])

    def cue_input(self, symbols: np.ndarray) -> np.ndarray:
        """The trial's input array: the cue at step ``0``, **nothing after it**.

        The zeros from step ``1`` on are what make the loop load-bearing rather than decorative -- with the cue held
        for the whole trial a decoder that ignored the state could read it off the drive, which is the sustained
        suite's situation and not this one.
        """
        symbols = np.asarray(symbols, dtype=np.int64)
        u = np.zeros((len(symbols), self.tau, self.n_neurons))
        u[:, 0, self.cue_neurons] = self.cue_templates[symbols]
        return u

    def action(self, x) -> "object":
        """The smooth action implied by a state, in ``(-1, 1)``, as a torch tensor of shape ``(batch,)``."""
        import torch
        idx = torch.as_tensor(np.asarray(self.action_neurons), dtype=torch.long)
        return torch.tanh(self.gain * x[:, idx].mean(dim=1))

    def feedback(self):
        """The callable the model adds to each step's input.

        Returns zeros at ``t = 0``, where the state is the zero vector and the cue's step has to stand alone.
        """
        import torch
        out = torch.as_tensor(np.asarray(self.feedback_neurons), dtype=torch.long)

        def fn(x, t):
            if t == 0:
                return torch.zeros_like(x)
            add = torch.zeros_like(x)
            add[:, out] = (self.scale * self.action(x))[:, None]
            return add

        return fn

    def summary(self) -> dict:
        return {"tau": self.tau, "n_symbols": self.n_symbols, "n_cue": int(len(self.cue_neurons)),
                "n_action": int(len(self.action_neurons)), "n_feedback": int(len(self.feedback_neurons)),
                "scale": self.scale, "gain": self.gain,
                "cue_sha1": _sha(self.cue_neurons), "action_sha1": _sha(self.action_neurons),
                "feedback_sha1": _sha(self.feedback_neurons)}


def _sha(idx: np.ndarray) -> str:
    import hashlib
    return hashlib.sha1(" ".join(str(int(x)) for x in np.sort(np.asarray(idx))).encode()).hexdigest()[:12]


def make_env_task(env: CueActionEnv, name: str, symbols, n_train: int, n_test: int,
                  readout_neurons, class_offset: int = 0, seed: int = 0):
    """One task inside the environment: the cue drawn from ``symbols``, read out from ``readout_neurons``.

    The task's ``u`` is :meth:`CueActionEnv.cue_input` -- a pulse at step ``0`` and nothing after it -- and its
    label is the cue. Every task built this way shares the environment, so a suite of them is three cue sets in
    **one** world and the loop is the same function for all of them; that is what lets a runner wire the feedback
    in one place rather than per task.
    """
    from .tasks import RateTask
    rng = np.random.default_rng(seed)
    symbols = np.asarray(symbols, dtype=np.int64)
    y_tr = rng.choice(symbols, size=n_train)
    y_te = rng.choice(symbols, size=n_test)
    return RateTask(name=name,
                    input_neurons=np.sort(np.concatenate([env.cue_neurons, env.feedback_neurons])),
                    readout_neurons=np.asarray(readout_neurons), n_classes=len(symbols),
                    n_neurons=env.n_neurons, tau=env.tau,
                    u_train=env.cue_input(y_tr), y_train=y_tr - class_offset,
                    u_test=env.cue_input(y_te), y_test=y_te - class_offset,
                    class_offset=class_offset)


class ClosedLoop:
    """The model with an environment wired to its own output: a drop-in for every call site in a runner.

    The feedback has to reach **every** forward pass -- training, evaluation, the Fisher blocks, the replay
    features -- or an arm would be measuring a different dynamical system from the one it trains. Threading a
    keyword through a dozen call sites is where a unit like this usually goes wrong, so this wraps instead:
    it is callable like the module and passes everything else through, which means ``model(U, None)`` at each
    existing site becomes the closed-loop call without being edited.
    """

    def __init__(self, model, feedback):
        self.model = model                      # set first: `__getattr__` reads it
        self.feedback = feedback

    def __call__(self, u, w_in=None):
        return self.model(u, w_in, feedback=self.feedback)

    def __getattr__(self, name):
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(name)
        return getattr(self.model, name)


def build(circ, readout_subset=None, n_symbols: int = 2, tau: int = 12, n_cue: int = 12,
          n_action: int = 8, n_feedback: int = 12, seed: int = 0, scale: float = 1.0,
          gain: float = 1.0) -> CueActionEnv:
    """Draw the three populations disjointly and the cue templates, all from ``seed``.

    ``readout_subset`` is the decoder's own draw and is **not** available to the environment: the action is read off
    a set drawn here, so the agent's action channel and the quantity a probe decodes are not the same neurons. That
    is deliberate -- an action read off the probe's own inputs would make the loop and the read-out one object.
    """
    rng = np.random.default_rng(seed)
    pool = np.arange(circ.n_neurons)
    if readout_subset is not None:
        pool = np.setdiff1d(pool, np.asarray(readout_subset))
    picked = rng.choice(pool, size=n_cue + n_action + n_feedback, replace=False)
    cue, action, feedback = np.split(picked, [n_cue, n_cue + n_action])
    return CueActionEnv(n_neurons=circ.n_neurons, tau=tau,
                        cue_neurons=np.sort(cue), action_neurons=np.sort(action),
                        feedback_neurons=np.sort(feedback),
                        cue_templates=rng.standard_normal((n_symbols, n_cue)),
                        scale=scale, gain=gain)
