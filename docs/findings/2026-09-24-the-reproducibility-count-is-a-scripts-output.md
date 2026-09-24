# The reproducibility count is now a script's output, and its new check finds today's controls automatically

**Date:** 2026-09-24
**Script:** `experiments/e103_reproducibility_audit.py`, **extended with an arm-overlap check** — and re-run.
Artifact: `runs/e103_reproducibility_audit.json`.
**Why it is a unit:** §9 of the paper carried the sentence *"of the 204 artifacts under `runs/` that carry a
`config`, 38 are run artifacts, they hold 35 distinct configurations, and 2 of the 35 have ever been executed more
than once"* — prose numbers, in a section whose whole argument is that a reproducibility claim must be a
measurement. The script that makes that measurement exists (`e103`), so the sentence can be its output.

---

## 1. What the script says now

| | |
|---|---|
| artifacts carrying a `config` (as `e103` counts them) | **303** |
| **configurations executed more than once** | **10** |
| of those, groups where **every** present arm is identical | **8** |
| of those, groups with at least one arm differing | **2** (both in the `e101`/`e102` family: the five-run `--fisher-batches 8` group where **5 of 5 arms differ**, and the `--fisher-batches 128` pair where **3 of 5** do — `ewc-block`, `ewc-block-rand`, `replay`) |

**The two censuses are not in conflict, they count different things**: §9's 204/35/2 came from a census of *run
artifacts of the rate-network line*, and `e103` counts every artifact that carries a config and has arms to
compare. The paper now states both with their definitions rather than reconciling them, because the second is
reproducible by one command and the first is not.

**And the *instrumentation* repeats are the strong ones**: the seven-run and four-run groups are
**identical to the last digit** on every present arm, because what differs between their members is only which
diagnostics were recorded (`interference`, `theta_drift`) — so of the ten repeated configurations, **eight
reproduce exactly and two do not, and the two that do not are the ones where the command was re-run rather than
the instrumentation changed**.

## 2. The new check: shared arms across *different* signatures

`group_repeats` groups by the **whole** config signature, so a re-run that adds a method — or changes a setting
the compared method cannot read — is a different configuration to it, and its overlapping arm is never compared.
**That is exactly the case this project's controls rely on** (`e140`'s C0a and C0b probes, `e146`'s bit-identical
tell), and each of those was established by hand in its own fire.

The extension pairs artifacts by **shared arm + shared `seed0`/`repeats`** regardless of signature:

| | |
|---|---|
| pairs compared | **3,294** |
| **identical** | **283** — `naive` 236, `replay` 29, `ewc` 10, `ewc-block` 4, `ewc-block-rand` 4 |
| differing | 3,011 |

**And it finds every one of the session's hand-established controls without being told about them**:

| pair | arm(s) found identical |
|---|---|
| `e140` plastic vs `e133` — **C0a** | **`ewc` and `naive`**, both n = 40 |
| `e140` frozen vs `e125` — **C0b**, four unread settings | `naive`, n = 40 |
| `e146` (λ = 3e-4, frozen) vs `e125` | `naive`, n = 40 |
| `e155` read-out 128 vs `e116` (same read-out) | `naive`, n = 40 |
| `e155` read-out 700 vs `e116` (same read-out) | `naive`, n = 40 |

**So rule 39's benign twin — "an arm agrees exactly with one whose settings it cannot read" — is now a scan
rather than a hand check**, and the five instances above were each paid for by a dedicated fire.

## 3. And what it cannot do, which is why the count is 283 and not 5

**The check cannot tell "should agree" from "should differ".** Of the 3,011 differing pairs, most are
*legitimately* different configurations that happen to share an arm name and a seed stream — a `naive` arm at
read-out 32 against a `naive` arm at read-out 128 is a different benchmark, and they are counted here as a
differing pair for no reason. Symmetrically, most of the 283 identical pairs are arms that cannot read the field
that differs (`--fisher-batches` for `naive`), which is true and uninformative.

**The sharp version needs a per-method table of which settings each method reads** — the runner's code implies it,
the artifacts do not state it — and until that exists this check is a **finder** (it surfaces the pairs worth a
human's attention) rather than a verdict. That is the same division of labour as `e158`'s corrections index, and
it is stated rather than hidden because a scanner that convicts is worse than one that lists (rule 22).

## 4. What this cannot settle

- **`e103`'s grouping is by exact signature**, so the ten repeated configurations are a **lower bound**: a
  configuration whose two executions differ in any recorded field is invisible to the group check, which is the
  gap the overlap check opens and only partly closes.
- **It reads artifacts, and artifacts record what the runner chose to write**: `e140` and `e144` lack the
  `partition_seed` key entirely (they predate the flag), so a pairing that depends on that field cannot be checked
  from them — and `e103`'s `missing_keys` block lists seven such artifacts.
- And the two groups that fail to reproduce are **the same family** (`--fisher-batches 8` and `128` re-runs) whose
  failure §9 already discusses with its own mechanism (thread count and the environment), so this extension adds
  no new failure — what it adds is that the *passes* are now found automatically.
