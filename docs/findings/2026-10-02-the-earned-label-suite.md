# The earned-label suite: the world is forgotten by 0.3333, and replay cuts that by 0.2188 at 3.27 sigma

*2026-10-02. `experiments/e352_the_earned_label_suite.py` trains two arms over five seeds on three sequential tasks
through one world, with one head per task and the read-out in the environment. Five minutes. Writes
`runs/e352_the_earned_label_suite.json`.*

## 1. One task became a sequence

`e349` to `e351` built a task whose answer exists **only in the environment**: the head reads the world's own state,
the world is driven by the agent's own actions, and unwired it is at rest -- so its read-out is a constant and the
accuracy is chance. That is one task, and every unit in this chain before those three read a *single* task through
the model's own state.

**This unit runs the corpus's protocol on it.** One world, three tasks of four cue symbols each, an eight-dimensional
world state read by one small head per task, and the body trained through the tasks in order. After each task every
task seen so far is measured, so the retention matrix comes out the way the corpus's runners produce it and
`mean_forgetting` is the same quantity: `mean_j (R[j, j] - R[T-1, j])` over the tasks before the last. Two arms:
**`naive`** trains each task in turn and nothing else, and **`replay`** keeps sixteen examples per finished task and
adds a cross-entropy term on eight of them to every step, through those tasks' own heads. Nothing else differs.

## 2. The answer

| read | mean over 5 seeds | sem |
|---|---|---|
| `naive`, diagonal | 0.8153 | |
| `naive`, `mean_forgetting` | **0.3333** | 0.0575 |
| `replay`, diagonal | 0.7875 | |
| `replay`, `mean_forgetting` | **0.1146** | 0.0397 |

**T1 MET**: one world and one set of populations across both arms, with one distinct fingerprint each for the world's
maps, the leak, the cue, the action and the feedback; the buffer is the only difference. **T2 MET**: the suite is
learned -- the worse arm's diagonal mean is **+0.5375 above a chance of 0.25**. **T3 MET**: the earned-label suite
**forgets**, by **0.3333** on `naive`. **T4 MET**: the buffer cuts it by **0.2188**, and paired within a seed the
five deltas are `[-0.4375, -0.1875, -0.0625, -0.1146, -0.2917]` -- **all five negative, 3.27 sigma**.

**The retention matrices say the same thing in the corpus's own shape.** On seed 0, `naive` learns task 0 at
**0.833** and reads it at **0.042** after two more tasks, while `replay` holds the same entry at **0.708**. Averaged
over the seeds, task 0's final accuracy is **0.3875** under `naive` against **0.6708** under `replay`.

**And the buffer is not free**: the diagonal is **0.7875** under `replay` against **0.8153** under `naive`, so the
0.2188 of retention costs **0.0278** of acquisition -- the trade the corpus's own method tables report, now on a
task whose answer lives only in the environment.

## 3. What it means for the benchmark the user asked for

A game-like continual-learning benchmark on this connectome needs three things: an agent that acts, a world whose
state is the consequence of those actions, and a method contrast in the corpus's units. `e348` to `e351` measured the
first two -- the world carries the cue, a body can write into it, and the width of the carrier is what the price was
-- and this unit adds the third: **the standard CL shape, with `naive` forgetting a third of its accuracy and a
sixteen-example buffer taking two thirds of that away, at 3.27 sigma over five seeds.** The suite is small and the
loop is local, but the object exists and it behaves like a benchmark rather than like a demo.

## 4. What it cannot do

*A bespoke loop and two arms*: the optimiser, learning rate, step count, batch size and buffer size are the corpus's,
but the loop is written here rather than taken from the runner, and `ewc`, the block penalties, the matched-random
control and the frozen controls are not run -- so this is a benchmark's **shape** on the earned label and not a
method comparison, and none of its numbers is comparable with the corpus's artifacts. *Three tasks and five seeds*:
a six-entry lower-left block is a small object, and the 3.27 sigma rests on five paired differences. *One world, one
leak and one width*: `leak = 0.35`, eight dimensions, four symbols per task, and `e351`'s finding that the width is
88% of the carrier's value and its channel's shape a seventh. *And the head is per task*: this is task-incremental,
so which task the trial belongs to is given to the read-out -- a shared head over one world is the harder
class-incremental benchmark and is not run here.
