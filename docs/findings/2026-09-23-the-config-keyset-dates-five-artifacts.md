# `e103`: two checks that should have been scripts, and the corpus number that explains the week

**Date:** 2026-09-23
**Script:** `experiments/e103_reproducibility_audit.py`; artifact `runs/e103_reproducibility_audit.json`; tests
`tests/test_reproducibility_audit.py` (14 cases).
**Artifacts:** `runs/e103_reproducibility_audit.json`, `runs/e101_rate_fb8.json`,
`runs/e102_rate_fb8_rerun.json`, `runs/e102_rate_fb8_rerun2.json`, `runs/e101_rate_fb128.json`,
`runs/e102_rate_fb128_rerun.json`, `runs/e8_hardened_basis.json`.
**Setup:** a scan of every `runs/*.json` carrying a `config`; no circuit is run, so the units below are
artifacts and configurations rather than neurons.
**Context:** `docs/findings/2026-09-23-the-fisher-free-arm-was-not-fisher-free.md` — an arm assumed invariant
that was not, and an artifact dated by its `mtime` that the migration had overwritten. Both were found by hand,
days late, and both were checkable from the artifacts alone.

---

## 1. The two checks, and what the first drafts of them got wrong

**Check A — does an arm reproduce?** Group the artifacts by `config` (minus `json_out`, the one key two runs of
one command must differ in), and where a configuration was executed more than once, compare each arm's
`replicates` **as a value**. Movement is reported separately rather than folded into the verdict, because rule
21 measured that the torch path is environment-shaped at about the fourth digit.

**Check B — does an artifact predate its runner's parser?** Within an artifact family (the leading `e<N>` of
the filename), take the maximal keyset as the reference and report what each artifact lacks. A runner that
dumps `vars(args)` cannot omit a flag its parser defines, so a missing key is a flag that did not exist yet;
`mtime` cannot say this, because `e98`'s in-place normalisation rewrote seven artifacts and left them one
timestamp.

**And the drafts are worth recording, because both failed the way this week's findings keep failing.** The
first version of check B used *key overlap* to define a family, and reported **50 artifacts** as predating a
flag — nearly all of them from other runners whose configs simply carry different keys. The second version
restricted to filename families but still dated **aggregate artifacts**, reporting
`e96_fisher_batch_sweep.json` as missing twenty-four flags; its `config` has three keys and is a hand-built
summary, so the question was being asked of the wrong object. The shipped version asks only what it can answer:
**artifacts that carry per-arm results** (a benchmark dump), within a family of at least three. It reports
**5** rows. A check that reports 50 rows none of which matter is worse than no check, because it teaches the
reader to skim it.

## 2. Check A, and the corpus number

| | value |
|---|---|
| artifacts under `runs/` with a `config` | **204** |
| of those, run artifacts (they carry `methods`) | **38** |
| distinct run configurations | **35** |
| **configurations executed more than once** | **2** |
| both of them | `--fisher-batches 8` (3 runs) and `128` (2 runs), **both from this session** |

**So before this session, none of the thirty-three once-run configurations had a second execution**, and the
project's reproducibility claims were prose for the simple reason that the corpus held nothing to check them
against. That is the number behind the week's error: `e101` inferred an environment difference from a single
pair of values because a second execution of the *same* configuration was not something the record contained.
`e103` makes the question one command instead of one insight.

Where a second execution exists, the answer is per-arm:

| configuration | arms identical | arms differing | movement |
|---|---|---|---|
| `--fisher-batches 8`, 3 runs | `naive`, `ewc` | `ewc-block`, `ewc-block-rand`, `replay` | 0.0062, 0.0125, 0.0167 forgetting |
| `--fisher-batches 128`, 2 runs | `naive`, `ewc` | `ewc-block`, `ewc-block-rand`, `replay` | 0.0208, 0.0104, 0.0167 forgetting |

**The pattern is identical at both batch counts, and it is the one `e102` found by hand**: the two arms that
anchor nothing estimated — no anchor at all, and a 26,568-entry diagonal — reproduce exactly, and the three
whose numbers the network line's conclusions rest on do not. Note that this is *not* what the audit could have
told anyone in advance: it needed the second execution to exist.

## 3. Check B, and the independent agreement

| artifact | lacks | the flag was added | so it predates |
|---|---|---|---|
| `e8_rate.json` | 11 keys incl. `basis`, `fisher_batches` | 09-22 **07:30**, 08:09 | the basis machinery itself |
| `e8_basis.json` | `shared_head`, `readout_size`, `classes`, … | 09-22 **09:41**, 10:18 | the shared head |
| `e8_fisher_batches.json` | `shared_head`, `readout_size`, `frozen_body`, `classes`, … | 09-22 **09:41**, 10:18 | the hardening |
| `e8_tuned_lambda.json` | *(same seven)* | 09-22 **09:41**, 10:18 | the hardening |
| `e8_class_incremental.json` | `readout_size`, `frozen_body`, `classes`, … | 09-22 **10:18** | the read-out narrowing |

Flag introduction times, read from the parser's own history: `basis`/`normalise_fisher`/`pool_below` **07:30**,
`fisher_batches` **08:09**, `shared_head` **09:41**, `readout_size`/`frozen_body`/`classes`/`input_overlap`/
`noise`/`support` **10:18**, `replay_batch` **11:48**, `pool_buckets` **18:36**.

**And this agrees with an audit that used a completely different mechanism.** `e8_fisher_batches.json` is the
artifact the paper's §4.7 table was attributed to, and the earlier value-based audit found its stored rows are
**replicate #0 of a three-replicate run** whose numbers match no cell of the sweep
(`docs/findings/2026-09-23-the-fisher-batch-sweep-is-a-stitch-of-first-replicates.md`). Independently, this
keyset check puts it **between 08:09 and 09:41 on 09-22** — that is, **before `576faec`, the commit whose whole
subject is that the benchmark had been measuring its decoder and that narrowing the read-out is what makes the
weights load-bearing**. So the artifact behind that table is on the *unhardened* benchmark, arrived at from
the flags rather than from the numbers, and the two methods agree.

**The limiting case is the one that matters.** The reference for that family is `e8_hardened.json` and
`e8_hardened_basis.json` — the **newest on disk**, and one of them is the artifact behind §4.7's table — and
they still lack `replay_batch` and `pool_buckets`. So the check is *relative to what has been run*, and the
newest artifact of a family can still predate the current parser. That is exactly why rule 27's check is not a
substitute for a reproduction run: a keyset says which code epoch an artifact came from, and never whether the
arm would come out the same if it were run again.

## 4. What this does not do

- **It does not date an artifact against the current parser**, only against the newest artifact of its own
  family on disk. The exact version needs a registry mapping runners to parsers, which this project does not
  have; inventing one here would be a larger change than the audit.
- **It does not detect an unreproducible arm in advance.** It reports a difference after two runs exist, so it
  would have caught `e102`'s question at the moment the second run finished and could not have raised it
  earlier.
- **It does not compare to four significant digits.** The verdict is exact equality; the movement columns carry
  the rest. Tightening the verdict to a tolerance would fold rule 21's environment component into a pass.

## 5. What follows

- **`e101`'s misdiagnosis is now a script's output rather than a paragraph's advice.** The lesson of this
  session — *a control is a control only in the process where you checked it* — required noticing that an arm's
  value had moved; `e103` prints, for every repeated configuration, which arms moved and by how much.
- **The paper's §9 can state the network line's reproducibility as a measurement** rather than as a
  qualification: 35 configurations, 2 ever executed twice, and the per-arm answer at both.
- **And the honest priority the corpus number implies**: with 33 of 35 configurations run once, a second
  execution of any of them is cheap and is the only thing that upgrades its numbers from *measured* to
  *reproduced*. Three ran twice today, by the accident of this session's repairs.

---

## 6. Correction: the audit's verdict was a statement about the schema, not about the arm

**Found by running `e103` on a corpus that had grown, four fires after it was written.** The five fires that
built `theta_drift`, `interference` and `second_order` put those fields **into the replicate records**, and
`arm_matches` was comparing `json.dumps(entry["replicates"])` — the **whole** record. So for the seven
executions of the whole-state `naive` configuration, whose forgetting is identical to six decimals, the audit
reported:

```
naive   DIFFER   move 0.0000 forgetting, 0.0000 accuracy   [0.047917, 0.047917, ... ]
-> 1 of 1 arms do not reproduce: naive
```

**A movement of exactly zero beside the words "do not reproduce"** — a verdict read off the wrong object, which
is the failure this module exists to catch one level up. The comparison is now over a **declared** field list
(`ARM_FIELDS`), and any key a member carries beyond it is reported **separately as instrumentation**, so a new
measurement added to the runner shows up as a note rather than as an unreproducible arm:

```
naive   identical move 0.0000 forgetting, 0.0000 accuracy   [0.047917 x 7]
        (instrumentation recorded beyond the arm fields: interference, theta_drift)
```

**Two consequences, and the second is the one worth keeping.**

- **The bug is the same shape as the ones the module was built for**, and it took *four fields of new
  instrumentation* and a corpus of seven repeats to expose it — a check is only as good as the corpus it is run
  on, and this one had two repeats when it was written.
- **The reproducibility result is now stronger than the paragraph above claims.** The three plastic
  `naive`-at-fixed-read-out configurations have **seven executions each** (the `e104` plastic run, `e106`'s three,
  and one each from `e107`, `e108`, `e109`), and **every one is bit-identical in forgetting and accuracy** —
  `0.047917`, `0.033333` and `0.072917`. So §5's "2 of 35 configurations have ever been executed more than once"
  is now **7 of 238 artifacts' configurations**, and the arm-level answer for the reproducible family is seven
  executions rather than two. The corpus number was a snapshot of a set that grows, which rule 17 already says
  to date rather than to quote.

**And the two families are now cleanly separated in the audit's own output**: the five-arm Fisher configurations
report `DIFFER` on three to five arms with movements of 0.006–0.040, and the `naive`-only fixed-read-out
configurations report `identical` on seven executions with a movement of exactly `0.0000`. **The arms whose
computation is shortest are the ones that reproduce**, which is the ordering `e106` found by hand and the audit
now prints.
