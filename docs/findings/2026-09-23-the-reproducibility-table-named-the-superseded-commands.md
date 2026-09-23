# The reproducibility table named the commands behind the superseded numbers

**Date:** 2026-09-23
**Method:** each of §9's six rows run through `--help` to confirm its flags exist, then checked against what the
section it names actually cites.
**Context:** `docs/findings/2026-09-23-the-limitations-section-was-more-severe-than-the-results.md`, which ended
by naming §9 and §8 as the remaining unread prose; `e97`, which established that every structured surface of
the corpus is clean.

---

## 1. The syntax was fine and the references were not

All five modules the table names import, and **every flag it uses exists** — `--json-out`, `--ladder`,
`--no-realized`, `--min-size`, `--seeds`, `--draws`. So a check on the commands' *form* passes completely. A
check on their *content* does not:

| row | problem |
|---|---|
| §4.3 control-draw spread | names `e12_control_spread --min-size 1 --seeds 2 --draws 5`, which is the **original 1.1e-3 measurement that §4.3 then refutes**; and it has **no `--json-out`**, so it leaves no artifact — the only row of six that does not, in a table whose preamble says every number is "recorded in the corresponding `runs/*.json`" |
| §5 | names `e6_predictor`, whose output is the **unpaired** σ that §5 itself says is "an order of magnitude too large" and supersedes with per-seed storage |

So **two of six rows told a reader how to reproduce the paper's *pre-correction* values.** That is the same
failure the repository held two of last fire — a script and a diagnostic disagreeing about a published number
— one level up, in the section that exists to tell a reader what to run. And it is worse here than in either of
those, because a reader who follows it has no reason to doubt the result: they ran the documented command and
got a number.

## 2. The fix, and the design choice in it

Each row now names its **artifact** as well as its command, so the output can be checked rather than assumed,
and the two stale rows say what they are:

- the control-draw row is labelled the **first** measurement and says outright that it leaves no artifact and
  is the figure §4.3 refutes, with the two commands that produce the *current* per-rung sds (`e86`'s protocol
  for the two other circuits, and `e67`/`e17`/`e17b` for d = 1307) given beside it;
- §5's row becomes the **three-step chain** that actually produces the published count
  (`e6_predictor --seeds 6` → `e64_predictor_per_seed` → `e94_predictor_denominators`), with the unpaired
  command kept as a labelled separate row.

**And the `--json-out` omission is the tell.** A row of a reproducibility table that names no artifact cannot
be checked by the reader it is written for, and its absence is invisible in a table where the other five rows
have one — the same class as `e98`'s finding that a diagnostic's "before" column must be reconstructible
rather than read from a live producer. **A command whose output goes nowhere is a claim with no evidence
attached, in the one place whose entire purpose is attaching evidence.**

## 3. Why a form-check on a command table is not enough

This is the third check this week that passed on *form* and failed on *content*, and the pattern is worth
naming because it is the natural way to audit a table of commands:

- `e97`'s existence and config checks pass on a corpus whose one known defect is a sentence;
- `e98`'s strict-JSON test passes on writers whose payloads merely happen not to contain `NaN`;
- and `--help` passes on six rows, two of which document the wrong number.

**In each case the check verifies that something is well-formed and says nothing about whether it is right.**
The instrument that catches all three is the same and is not mechanical: run the command, read its artifact,
and compare it with the claim the row is attached to — which is what §9's table now makes possible by naming
the artifact beside the command.
