# The loop closes

*2026-10-01. Runs: `experiments/e325_the_loop_closes.py --json-out runs/e325_the_loop_closes.json` -- two circuit
sizes, the frozen connectome network, the corpus's own 32-neuron read-out draw. Minutes. Plus
`clfly/network/env.py` and an optional `feedback` argument on the model's forward pass.*

## 1. The other half of what `e322` named

`e322` measured that a sustained stimulus makes the trial's time axis carry nothing, and named two ways to give it
one: **a writer whose value changes with the step**, which `e323` built and `e324` trained the five arms on, and
**an environment in the training loop**. This is the second, and it is the one that was still missing when `e324`
ended with *"nothing here closes a loop: the sequence task's input still does not depend on the agent's output, so
this is the benchmark's first temporal task and not yet a game."*

**The contract is one callable.** `ConnectomeNet.torch_model()`'s forward pass takes an optional
``feedback(x, t) -> (batch, n)`` whose value is **added** to the step's input, where ``x`` is the state before that
step's update. So the agent's own activity at step ``t - 1`` is part of its input at step ``t``, and because the
addition is a torch operation the loop is differentiable: backprop-through-time crosses it exactly as it crosses
the recurrence. ``feedback=None``, the default, leaves the computation **bit-identical** to the open-loop version
every artifact in this repository was written through -- asserted by test, not by argument.

**And the world is the smallest one that needs a loop.** `CueActionEnv` shows a cue at step ``0`` and takes it
away; from step ``1`` on the only thing in the input is the agent's own last action, read off eight of its neurons
and shown back at twelve others, drawn disjoint from the cue channel **and from the decoder's own read-out draw**,
so the loop and the probe are not one object. The trial is a delayed report of a cue that is gone, under feedback
from the report's own machinery.

## 2. Four claims, all met

**T1 MET.** The feedback term is non-zero at some step, largest **0.5670** -- the action reaches the agent's own
input.

**T2 MET, and the loop is not a detail.** The closed and open trajectories of the same network on the same inputs
diverge by **52.04%** of the peak state at `mb+cx+al@n952` and **31.40%** at `n1307`. A third to a half of the
state is being rewritten by the agent's own action.

**T4 MET.** Restricted to the decoder's own 32 neurons, the last-step divergence is **12.48%** and **9.36%** of the
peak -- so the loop does not merely move the state somewhere the read-out cannot see: it moves **what the decoder
is looking at**, by around a tenth of the state's own scale.

**T3 MET, and it is the ceiling that is the interesting part.** The cue probe reads **1.00** at every step from
step 1 on, in **both** loops, and the last-step margin is **+0.50** above chance. The frozen connectome reads this
cue trivially: twelve cue neurons, one recurrent step, and a 32-neuron read-out is enough. So the loop rewrites
half the state and a tenth of the read-out, and leaves the task's own answer untouched.

**That saturation is why T4 is written the way it is.** The first registration measured the loop by the probe's
**accuracy margin**, a quantity bounded above by 1.0 that is already at its ceiling here: a "moves by 0.04" claim on
it had no room on the upside and could only fire, whatever the loop did. It was corrected **before** the registered
run, on a smoke run at a non-registered configuration that showed the 1.00, and the corrected quantity is the
divergence restricted to the read-out, which has headroom and asks what the accuracy claim was about. This is the
same class as `e323`'s T3, which was registered on a quantity whose floor sat above its own bar.

## 3. What that says

**A game is now buildable here, and this unit does not build one.** The pieces are: an environment whose next input
depends on the agent's last output (this), a differentiable path through it (this, and asserted bit-identical when
off), and a temporal task the recurrence has to carry (`e323`). What is missing is the thing that makes it a game
rather than a loop: **a reward and a policy**. Nothing here trains on the loop, so all four claims are the frozen
substrate's behaviour.

**And the loop needs a task it can matter for.** On this environment the answer is already in the read-out at
ceiling, so a tenth of divergence in the read-out costs nothing. A closed loop is only worth closing where the
read-out has headroom -- which is the same sentence `e322` produced from the other direction, and the same one
`e324` produced when the sequence suite's accuracy fell by 0.21 while its forgetting did not rise.

## 4. What it cannot do

**The network is frozen**, so nothing here says a loop can be learned in, or that BPTT through it converges -- only
that the gradient path exists and that ``feedback=None`` is untouched. **The action is smooth**: a ``tanh`` of the
mean activity over eight action neurons, chosen so the loop can be differentiated through; a hard threshold is a
one-word change and is not measured, and it would make the loop non-differentiable and the trajectory piecewise.
**One draw of the three populations, one scale, one gain**, both at 1.0: whether a tenth of read-out divergence
grows or vanishes as the feedback is turned up is a knob and not a sweep here. **The probe is linear**, and the
cue's ceiling means T3 has no power to detect anything but destruction. **Two circuit sizes and one cue width**:
the cue is twelve neurons against a 952- or 1307-neuron circuit, and a wider or narrower cue changes how much of
the read-out it occupies. **And the environment is memoryless in the world and not in the agent**: the cue is
random per example and the world has no state of its own, so the loop is the only thing that makes step ``t``
depend on step ``t - 1``.
