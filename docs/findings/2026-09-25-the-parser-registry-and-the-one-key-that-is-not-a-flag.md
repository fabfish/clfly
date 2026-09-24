# The registry `e103` asked for: every artifact's author, read from the AST — and the one key that is not a flag

**Date:** 2026-09-25
**Script:** `experiments/e172_parser_registry.py` — analysis only, no runs. Artifact:
`runs/e172_parser_registry.json`.
**Answers:** `e103`'s docstring, which names the general form it could not reach — *"the general check would take
each runner's parser as the reference; that needs a registry this project does not have"* — and it is the first
**test** of the premise both `e103` and rule 47 rest on.

---

## 1. The registry, built statically

For each of the **76** `experiments/*.py` files that define argparse flags, the flag names are read from the
**syntax tree** — `add_argument("--flag", …)` calls with a string literal — so the registry describes the parser's
*source* rather than whatever a module does at import time. Dashes become underscores, because that is what
`vars(args)` does.

A `config` is `vars(args)`, so a runner **could have written** an artifact exactly when its parser defines **every
key** the artifact carries. That gives an authorship test with no filename heuristic in it:

| | artifacts |
|---|---|
| a single possible author | **289** |
| more than one (a small config matches several parsers) | 15 |
| **no possible author** | **4** |
| total carrying a `config` | 308 |

## 2. The premise, tested: no flag has been removed

Both `e103` and rule 47 assume **a parser only ever gains flags** — stated many times, never checked. The
registry checks it: a `config` key that no current parser defines would mean either a **removed flag** or an
artifact from a runner no longer in the tree, and a removed flag is precisely the case rule 47's keyset dating
cannot see.

**All four unclaimed artifacts carry the same key, and the cause is not a removed flag**: each has `save_theta`,
which its own runner does not define.

| | |
|---|---|
| `e122_path_geometry`, `e124_barrier_12seeds`, `e130_barrier_r32`, `e131_barrier_r1307` | carry `save_theta` |
| `e122_path_geometry.py`, `e124_barrier_distribution.py` | define **28** and **32** flags, and **not** `save_theta` |
| `e8_rate_network.py` | **is** the only runner that defines `save_theta` as a flag |

**And the two runners write it themselves**: `args.save_theta = args.theta_dir` (`e122_path_geometry.py:270`,
`e124_barrier_distribution.py:56`). So the key in those artifacts is a **runtime-assigned synonym** for
`theta_dir`, and it was never an argument.

**Two conclusions, and they point opposite ways for the same fact.**

1. **The premise holds**: no flag has been removed, so `e103`'s keyset dating and rule 47's start-time correction
   are sound over this corpus — and now that is a *checked* statement rather than an assumed one.
2. **But `config` is not `vars(args)` of the parser alone**: it is whatever the namespace holds when it is dumped,
   and a runner may write into it. So containment-by-parser-keys is a **necessary and not a sufficient** authorship
   test, and the one key name that exposes it (`save_theta`) has two meanings in this tree — a flag in
   `e8_rate_network.py` and a synonym for `theta_dir` in two others. **A config key name is not a reliable
   identifier of provenance across runners**, which is the same shape as rule 46's finding that an identical
   `config` does not imply one partition.

## 3. What it adds to `e103`'s dating

`e103` dates an artifact by comparing it with the **newest artifact of its own filename family**, which is why its
docstring limits the check to run artifacts *within a family of at least three*: **it names 7 artifacts**. The
registry names **304 of 308**, against a parser rather than against a sibling — so the relative check can be
replaced by an absolute one, and a future artifact with an unexpected key is caught at once instead of when its
family happens to grow.

**And the 15 ambiguous artifacts are the honest part of the number**: a 1-key or 3-key config (the hand-built
summary artifacts) is contained in most parsers, so the registry reports the maximal candidate and says it is a
candidate rather than an author. 289 unambiguous + 15 ambiguous + 4 explained = 308.

## 4. What this cannot settle

- **The AST sees the file, not the library.** A flag added by a shared helper — or by a loop over a table of flag
  names — is invisible, and the fact that no such helper exists *today* is a property of the tree rather than of
  the method. The four unclaimed artifacts are explained by hand *because* the method cannot explain them.
- **It does not date anything.** It says which parser could have written an artifact, and the epoch it reports is
  "what today's parser has that this config lacks" — a *lower* bound on the artifact's age, since a flag can be
  added long after an artifact without the artifact changing.
- **15 artifacts have no single author**, and for those the registry's answer is a set, not a name.
- **Rule 47's premise is checked over this corpus and not in general**: a flag removed *and* added back, or one
  renamed, would leave no trace here — and `save_theta` shows that even an unchanged key name can mean two things.
