# The penalty arms were never non-reproducible: `e153` ran at `lam = 1.0` and `e144` at `3e-3`

**Date:** 2026-09-24
**What this corrects:** three artifacts written earlier the same evening — `e153`'s finding
(`2026-09-24-e153s-own-control-fails-on-the-three-penalty-arms.md`), the `§9` paragraph I edited to say the
wiring family breaks the fb32 reproducibility claim, and the mechanism note
(`2026-09-24-the-environment-and-the-seeds-do-not-explain-the-penalty-arms.md`). **All three were built on a
premise that one command's config check would have refuted.**
**Artifacts:** `runs/e144_r32_overlap1_methods_40reps.json`, `runs/e153_r32_overlap1_methods_40reps.json`.

---

## 1. The evidence, and it is one field

| field | `e144` | `e153` |
|---|---|---|
| **`lam`** | **0.003** | **1.0** |
| `fisher_batches` | 32 | 32 |
| `iters`, `lr`, `batch`, `readout_size`, `input_overlap`, `support`, `classes`, `noise`, `seed0`, `repeats` | 500, 3e-3, 32, 32, 1.0, 80, 4, 1.0, 0, 40 | identical |
| `methods` | `naive,ewc,ewc-block,ewc-block-rand` | the same four **plus `replay`** |

**`e153` is not a second execution of `e144`'s configuration: its penalty strength is 333× larger.** And that
explains every observation the three artifacts above were written to explain:

- **the three penalty arms differ** — they are the arms that read `lam`;
- **`naive` and `replay` are bit-identical** — they do not read it, so `lam = 1.0` is invisible to them;
- **the magnitude** (up to 0.229 per replicate) — a 333× stronger penalty, on a family whose λ dependence is
  already known to be non-monotone (`e141`'s sweep: 0.0654 at 3e-3, 0.0810 at 3e-2, 0.0846 at 3e-1 on the base
  family).

**So there is no evidence of penalty-arm non-reproducibility at all**, §9's `--fisher-batches 32` claim is not
contradicted by anything, and the mechanism note's question (nondeterministic accumulation or an unseeded draw)
has no phenomenon to explain. **The two candidates are still worth knowing about, and neither is implicated.**

## 2. Where the error entered, and it is a shape this project has a rule for

**The registration paraphrased the command and the paraphrase omitted `--lam`.** `e153`'s row in the programme
table reads *"`--input-overlap 1.0 --repeats 40 --methods naive,ewc,ewc-block,ewc-block-rand,replay`"* — with no
`lam` in it — and the registration's prose said *"identical flags plus a fifth method"*. **The launch then used
the paraphrase**, the runner's default is `lam = 1.0`, and **the C0a claim (per-replicate identity with `e144`)
was false when it was written** — not discovered to be false, *written* false, because the two artifacts' configs
were never compared before the claim was made.

**And the tell was available for free the whole time**: `e144`'s artifact carries `lam = 0.003` and `e153`'s
carries `1.0`, in a field the project's own `e103` reads for its signatures. **Two commands that are "the same
command" for the purpose of a control are same *config*, and this project had a script that says so.**

## 3. Rule 44

**A C0 identity claim — and any claim that a configuration has been executed twice — must be checked against the
two artifacts' `config` fields, not against a command as paraphrased in a registration.** The tell is that a
paraphrase omits flags: `e153`'s row named `--methods` and `--repeats` and not `--lam`, and the omitted flag is
the one the controlled arms read. **And the corollary is rule 39's benign twin read from the other side**: two
runs with *different* configs will still be bit-identical on every arm that cannot read the difference, so
**bit-identity is evidence about which fields the arms read and not evidence that the configurations are the
same** — which is why `e146`'s bit-identical artifact was a *tell* about a mistaken prediction rather than a
reproduction.

## 4. And one more instance of the same shape, found while checking

`e155` ran with **`lam = 1.0` and `fisher_batches = 32`** while its comparator `e116` has **`lam = 0.003` and
`fisher_batches = 8`**. Its arms are `naive` and `replay`, **neither of which reads either field**, so its
bit-identical `naive` rows are a genuine control — **of the arm, not of the configuration**. The finding that
called it *"a second execution of that configuration"*, and the §9 sentence that counted it among configurations
executed more than once, both overstate: **what was executed twice is the `naive` arm under a config whose two
unread settings differ.**

## 5. What this changes, and what it does not

- **`e153`'s numbers stand**: it is a valid five-method table on the wiring family **at λ = 1.0**, paired on its
  own forty seeds, and its P1/P2 verdicts (the biology's contrast against the three-draw mean; replay first) are
  about that artifact. What it is **not** is a second execution of `e144`.
- **`e159`**, running, was launched with the same command as `e153` and therefore **is** a genuine repeat of
  `e153`'s configuration — so it still answers "does this configuration reproduce?", at λ = 1.0 rather than at
  3e-3, and it will also be the wiring family's first λ = 1.0 table.
- **The three artifacts above are corrected in place** rather than deleted, and the §9 paragraph is restored to
  what it said before this evening's edit, with the two overstatements named.
- **And the lesson is not "be careful"**: it is that this project already had the instrument (`e103` reads every
  config), and the defect was writing a claim about two runs without running it. Rule 44 makes that a step.
