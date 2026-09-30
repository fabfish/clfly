# The corpus holds repeats: eleven clusters, seventeen files, and the two censuses that counted them twice

*2026-10-01 03:04. Runs: **none new** — `experiments/e301_the_corpus_holds_repeats.py` reads every artifact under
`runs/` and the three censuses' own readers, writing `runs/e301_the_corpus_holds_repeats.json`. Seconds.*

## 1. What arrived, and what it exposed

On 2026-09-29 the 1440-item suite of the read-out-32 frozen-bias configuration finished —
`runs/e287_frozenbias_suite1440_40reps.json` at 05:28 and `runs/e288_frozenbias_suite1440_40reps.json` at 05:31. They
are the same command. One launch was believed dead and a second was started; both finished, and both wrote.

That is a bookkeeping event, and it exposed an instrument question. Three of this line's censuses read the corpus as
`runs/*.json`, so they count **files**: `e286`'s sample-swap census went from 3 swaps to 7, `e295`'s comparisons from
26 to 28 and `e296`'s from 40 to 42. None of that is new science. The unit below finds how deep the problem goes.

## 2. The corpus holds eleven clusters, not one

The detector — `clfly.bench.corpus` — calls two artifacts **one experiment** when they agree on the `config` minus
the output path, on the eval size, on the three draw blocks, on the arm set, and on every shared replicate row's
training-derived fields with at least one of those fields actually present. It finds **26 pairs and 11 clusters**:

| cluster | files | what it is |
|---|---|---|
| `e102_rate_fb8_rerun` | 2 | a re-run kept beside its original |
| `e104_frozen_{r128,r32,whole}_plastic` | 4 each | four executions of one command |
| `e110/e111/e112/{readout,}_plastic` | 2 each | the `plateau` flag is not a field the runner reads |
| `e113_r300_draw1` | 2 | as above |
| `e153_r32_overlap1_methods_40reps` | 2 | **the corpus's largest reproduction**, 200 values |
| `e164_fb8_today_{a,b}` | 2 | two executions registered as one experiment |
| `e287_frozenbias_suite1440_40reps` | 2 | **the new one** |

**The corpus's file count stands seventeen above its experiment count.** Ten of the eleven clusters are the corpus's
*deliberate* reproduction record — the `e026` to `e103` to `e159` line built its "floor" out of exactly these — and
only the eleventh is an accident. The distinction matters and the detector cannot make it: what it reports is a
duplicate, not a mistake.

## 3. And a repeat is bookkeeping, not a difference

For **every one of the 26 pairs** the two payloads agree on every key outside four: `config.json_out` (where the
runner was told to write), `cpu_time_s` and `timing_s` (how long the machine took) and `code_revision`/`environment`
(which files were untracked and how fast the box was when it started). Nothing else differs — not one arm, not one
replicate, not one metric. **R2 holds for 11 of 11 clusters.**

So the `e287`/`e288` pair is `e301`'s own confirmation of what `e159` established at 200 values: the same command,
executed twice, gives the same answers to every digit the artifact carries, and the executor's clock is the only
thing that moved.

## 4. The repair, and the licence for it

`clfly.bench.corpus.repeat_paths` returns the non-canonical member of each cluster, and the three censuses now skip
it. The counts move and **no verdict changes class**:

| census | kept | dropped |
|---|---|---|
| `e286` candidates / swaps / comparisons | 34 / 7 / 54 | **23 / 5 / 34** |
| `e295` comparisons per metric | 28 | **24** |
| `e296` comparisons per metric | 42 | **38** |

`e286`'s X1 stays MET and its X2, X3 and X4 stay FIRED; `e295`'s B1, B2 and B3 stay MET; `e296`'s C1 and C3 stay
FIRED and its C2 stays MET. The largest moves are in the counts a reader would quote and not in anything a claim
turns on — which is why the fix is in the **reader** and not in the file, and why the second copy stays on disk.

**The repair was then extended to the five further censuses that glob the same directory** — `e267` (108 to 100
matrices, S1 to S3 MET), `e290` (279 to 246 arms, Q1 to Q3 MET), `e292` (279 to 246, S1 to S3 MET, and the r512
rung leaves the ladder because two of its six arms were second copies), `e294` (72 to 64 matched-pair blocks, P1 to P3
MET) and `e299` (304 to 271 arms, F1 to F3 MET, with the README's scope blockquote rewritten). **Every one of them
moved in its counts and in no verdict.** R3 was registered on the first three, so this is reported and not claimed:
the registration discipline is what makes the three a result and the five an observation.

## 5. What it cannot do

**The detector cannot tell two executions from one execution run twice**, and it should not try: with the seeds the
runner uses, a re-execution *is* a reproduction, which is exactly what the corpus's floor line needed. **Agreement is
required on six training-derived fields** and a pair can only pass by having trained identically; a payload with none
of those fields recorded cannot be called a repeat at all, which is what keeps two analytic artifacts from pairing.
**Canonicity is lexical** — the alphabetically first member is kept, and because every pair agrees everywhere any
other choice gives the same numbers, but the *name* a finding cites is a convention. **And a duplicate is not a
mistake**: ten of the eleven clusters are written up as evidence elsewhere, and this unit can only say that one
execution is not two.
