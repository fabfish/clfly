# The conformance contract: the field a reader needs most to trust a result is the one the corpus carries least

*2026-10-01 07:58. Runs: **none new** — `experiments/e309_the_conformance_contract.py` reads the corpus against the
eight fields `clfly/bench/conformance.py` declares, writing `runs/e309_the_conformance_contract.json`. Seconds.*

## 1. A protocol is a claim about what a result contains

The FlyCL v0 block calls its reference framework *"a shared protocol that CL-for-SNN work currently lacks"*. `e302`
and `e303` read the block's **metric list** and never asked the question that makes a protocol work: **can a reader
who is not the author recompute the numbers?** This unit writes that down as eight checkable fields — task list, seed,
eval size, `final_accuracy`, `mean_forgetting`, a retention matrix, a read-out draw fingerprint, a code revision —
each with the reason a third party needs it, and reads the corpus against them.

## 2. K1, K2 and K3 — the contract binds, and on the field `e103` named

| | |
|---|---|
| artifacts read (on `e301`'s collapse) | **547** |
| carrying **all eight** | **76 (14%)** |
| the **scarcest** field | **a read-out draw, 76 (14%)** |

**K1 MET**: a field the benchmark needs is carried by a seventh of the corpus. **K2 MET**: the scarcest field is the
**read-out draw fingerprint** — the one `e103`'s line argued for at length, so that a number can be attributed to the
draw it came from rather than to one recomputed after the fact. **K3 MET**: 76 of 547 artifacts (**14%**) are a result
a third party can recompute.

## 3. K4 — the record comes in blocks, not in degrees

| artifacts | how many of the eight they carry | what |
|---|---|---|
| 158 | **0** | nothing the contract asks for |
| 242 | **1** | a seed, and nothing else |
| 11 | 5 | the result block without the eval size, the draw or the revision |
| 28 | 6 | as above plus the eval size |
| 32 | 7 | as above plus the revision |
| 76 | **8** | the whole contract |

**K4 MET, and the shape of the table is the finding: no artifact carries two, three or four of the eight.** The corpus
has three kinds of payload and nothing in between — analyses with a seed, results with the five fields that make a
row of the methods table, and results that also say which sample and which epoch they are on. A reader who wants the
middle of the table does not get a gradient; they get an artifact that either has the block or does not.

## 4. What this is for

**It is the benchmark's side of the question `e302` and `e303` asked of the block's prose.** `e302` found two of the
block's five metrics have no artifact field; this says why that cannot be fixed by prose: a reader recomputing the
decomposed forgetting needs the **retention matrix**, which is exactly the block `e304` computes from and which the
242 seed-only artifacts do not have. **The contract is a deliverable and not an audit**: `clfly/bench/conformance.py`
is importable, so a runner can check its own output before writing it, and a benchmark can say what a submitted
result must contain.

## 5. What it cannot do

**The eight are this unit's selection from a reader's task**, and a benchmark that also wanted the per-task
observability spectrum or the pairwise principal angles would add rows and move the counts — K1 and K3 are claims
about a contract, and a different contract gives different numbers. **A predicate reads one spelling**: `seed0` under
`config` and a `tasks` list count, and a runner that recorded the same fact under another name would read as
non-conformant. **Conformance is not quality**: an artifact can carry all eight and be wrong, which is every other
unit's business. **And the census is over this repository's artifacts on `e301`'s collapse**, so it describes what
this project has written and not what a fresh run would produce.

## 6. RE-READ 2026-10-01 10:52 — the list is eleven, and the share did not move

`e313` found that the decomposition the block prescribes is already written down per task under `learned`,
`final_per_task` and `forgetting_per_task`, and that the retention matrix is the redundancy over them. That gap was
reported in §5 of that finding and left open; `e314` closes it: **the three fields are in the contract and the matrix
stays**, and the unit's claims are re-run over eleven.

**What moved: nothing.** The artifacts are **552** on the same collapse, **76 (14%)** carry all eleven, the scarcest
field is still **the read-out draw at 76**, and K1 to K3 hold with the same numbers they held at eight. Adding three
required fields could only have shrunk the conformant set, and it did not, **because the three ride with the matrix
they are the cells of** — the fields are carried by **147** artifacts each, more than a quarter.

**What sharpened: K4.** At eight fields the hole was two to four; at eleven it is **two to seven**, and the counts run
**0, 1, 8, 9, 10, 11**. The record is one of three things — nothing, a seed, or the result block and however much of
the rest — and never a partial result.

K1's and K4's wordings in this unit are now derived from the contract's length rather than written as "eight", so a
further addition does not leave them stale
(`docs/findings/2026-10-01-the-contract-with-the-result-block.md`).

**RE-READ 2026-10-03: K1 HAS FIRED.** The scarcest of the fields is now carried by **exactly a quarter** of the
corpus rather than under it -- 0.25 exactly, on 688 artifacts -- and the claim's falsifier was "every field carried
by a quarter or more", so the claim fires at its own boundary. What moved it is the window's runs: `e374` to `e379`
each wrote a closed-loop artifact, and every one of them carries the read-out draw as the rarest of the fields it
need not carry. The live test now reads K1's verdict off the artifact and pins its measured percentage rather than
demanding MET, as `e267` does for its own fired claims; the knife-edge `< 0.25` is replaced by `<= 0.25`, which is
the boundary the assertion was testing. K2, K3 and K4 stay MET and nothing else in the census moved: the scarce
field is still the read-out draw, the block structure is unchanged, and the share of the corpus that is a
recomputable result is still a small minority.
