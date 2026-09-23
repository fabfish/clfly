# The migration is not durable while the writers are not

**Date:** 2026-09-23
**Script:** `experiments/e98_strict_json_migration.py`; artifact `runs/e98_strict_json_migration.json`; test
`tests/test_artifact_writers.py`.
**Context:** `docs/paper/clfly-v1.md` §9 and `clfly/bench/artifacts.py`'s own docstring, both of which stated
this in numbers that were wrong.

---

## 1. The claims, and what they measure

§9 said **"seven rate-network artifacts"** were written in a form that `JSON.parse`, `serde_json`,
`encoding/json` and `pandas.read_json` all reject, and that **"every writer now goes through
`clfly.bench.artifacts.write_json`"**. `write_json`'s own docstring repeated the seven. Measured:

| claim | measured |
|---|---|
| seven artifacts refused by a strict parser | **13 of 216 (6.0%)** |
| all of them rate-network | **8 are; 5** (`e36`, `e38`, `e53`, `e56`, `e59`) carry `NaN` from a ratio |
| every writer goes through `write_json` | **10 of 42** modules that write anything; **32 use `json.dump` directly** |

So the first claim undercounted by six and mis-described two of the thirteen, and the second was true of
under a quarter of the writers. Both are the familiar shape — a count of a set that grew, and a claim about
"every" made from the subset that had been looked at — and both were **in a section whose whole subject is
whether this project's claims are checkable**.

## 2. The migration, and the check that no value moved

All thirteen artifacts were normalised in place through `write_json`, with the comparison made **under the
mapping that is the point of the exercise**: both trees have every non-finite value replaced by `None`
before they are compared, so the check asks whether the *numbers* moved rather than whether the spelling of
"not a number" did. **Every one of the thirteen was identical; a strict parser now refuses none of them.**

One of them matters more than the rest: `runs/e8_fisher_batches.json` is **the artifact behind the paper's
§4.7 table**, and until this fire `pandas.read_json` could not open it.

## 3. And it is not durable — demonstrated, not asserted

The debt is in the **writers**, not the files. Re-running `e38_variance_budget.py`, one of the 32 direct
writers, **restored all sixteen of its bare `NaN` tokens** — measured before and after, on a file the
migration had cleaned minutes earlier:

```
after e98 --write :  e38_variance_budget.json   bare non-finite tokens: 0
after re-running  :  e38_variance_budget.json   bare non-finite tokens: 16
```

So a migration of artifacts is a state, not a repair, and the honest sentence for §9 is *"the artifacts on
disk conform, and they will stop conforming the next time one of these 32 modules runs"*. This is the same
lesson as the previous fire's, one level over: there the fix belonged in the producer rather than in a
second script, and here the fix belongs in the writers rather than in the files they have already written.

## 4. The durable guard, and why it is a list rather than a rule

`tests/test_artifact_writers.py` pins the **exact set of 32 module names** and fails when a *new* module
writes with `json.dump`. Two design choices in it are deliberate:

- **It asserts set equality, not a bound.** A bound would let the list grow by one without anyone noticing;
  set equality means migrating a module also requires deleting its name, so the debt is a number somebody
  has to keep current. The friction is the point, because a list that updates itself is a list nobody reads.
- **It counts `ast.Call` nodes, not text.** My first count was a `grep`, and it reported `e98` itself as a
  direct writer — because `e98`'s docstring *discusses* `json.dump`. A text-based guard would have had the
  author of the guard on its own list; the AST version has 32 real calls and no false positives.

**And `e98` found one of mine**: `experiments/e92_grid_report.py`, written this week, called `json.dump`
directly. It happened to produce no non-finite values, so nothing was visibly wrong — which is exactly how
the debt accumulates. It now uses `write_json`, and the list is 31.

## 5. What is not fixed

**The 31 remaining direct writers are not migrated.** Every one of them is a module whose payload may or may
not contain a non-finite value, and which do cannot be known without running them — `e38`'s do, and two
others are known because their artifacts were in the thirteen. So the honest statement is a count and a
guard rather than a repair: **31 modules can write a non-conformant artifact, 13 artifacts were non-conformant
before this fire, 0 are now, and 1 became non-conformant again during it by being re-run.**
