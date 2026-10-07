# The eight that answered: five of them move a verdict, two never read the corpus, and one records none

*2026-10-08. `experiments/e465_the_eight_that_answered.py` takes the **eight** entries `e464`'s sweep found naming a path
under `runs/`, carrying `REFUSED` in their source and answering anyway, and runs **each of them twice** with its output
written outside the corpus -- once with this repository as the working directory and once inside a corpus-less copy of it
-- comparing the **claim verdicts the module writes for itself**. Four claims: **RB1 FALSIFIER FIRED**, **RB2 NULL**,
**RB3 MET** and **RB4 MET**.*

## 1. The eight, run twice

| the module | with the corpus | without it | moved |
|---|---|---|---|
| `e200_draw_confound_audit` | records no `claims` block | records no `claims` block | none |
| `e268_paper_supersession_audit` | Q1 FALSIFIER, Q2 MET, Q3 MET | Q1 FALSIFIER, Q2 MET, Q3 MET | **none** |
| `e302_the_benchmark_metrics` | M1 MET, M2 MET, M3 **MET**, M4 **FALSIFIER** | M3 **FALSIFIER**, M4 **MET** | **M3, M4** |
| `e322_the_benchmark_has_no_time_in_it` | T1 MET, T2 FALSIFIER, T3 FALSIFIER, T4 NULL, T5 **FALSIFIER** | T5 **MET** | **T5** |
| `e369_why_the_cliff_is_where_it_is` | P1 MET, P2 MET, P3 NULL, P4 MET | P1 MET, P2 MET, P3 NULL, P4 MET | **none** |
| `e392_the_game_card` | M1 FALSIFIER, M2 **MET**, M3 MET, M4 MET, M5 FALSIFIER | M2 **FALSIFIER** | **M2** |
| `e416_the_penalty_ledger` | AL1 **MET**, AL2 **MET**, AL3 **MET**, AL4 MET, AL5 **MET** | AL1/AL2/AL3 **FALSIFIER**, AL4 MET, AL5 **NULL** | **AL1, AL2, AL3, AL5** |
| `e452_what_a_fresh_clone_reports` | CY1 to CY4 MET, CY5 **MET** | CY5 **FALSIFIER** | **CY5** |

| claim | measured | verdict |
|---|---|---|
| RB1 the two arms are one configuration | **8 of 8** wrote an artifact in both arms, **8 of 8** pairs have equal key sets, **7 of 8** record claims in both | **FALSIFIER FIRED** |
| RB2 and most of the eight did not need the corpus | **3** of **8** write the same verdicts both ways, **38%** | **NULL** |
| RB3 and the rest answer a question their input cannot support | **5** of **8** move at least one verdict, of **7** that record any | **MET** |
| RB4 and the corpus arm is the gate's own reading | **7** of **8** have a gate artifact and **7 of 7** reproduce it | **MET** |

## 2. What the two arms say

**Five of the seven measurable eight move a verdict when the corpus goes, and the moves are the vacuous premise in its
purest form.** `e302`'s **M3** is MET with the corpus and FALSIFIER without it, `e392`'s **M2** the same, `e416`'s
**AL1**, **AL2** and **AL3** the same, and `e322`'s **T5** goes the other way, from FALSIFIER to MET. **And the direction
of the error is not even constant inside one module**: `e302`'s **M4** is FALSIFIER with the corpus and **MET** without
it, so one of that unit's claims is made true by the corpus's absence while another is made false by it, and a clone
that took its table would read a MET that the corpus refutes and a FALSIFIER that only the corpus supports.

**And two of the eight never read the corpus at all.** `e268` and `e369` write *identical* verdicts in both arms --
**Q1, Q2, Q3** and **P1 to P4** unchanged, including the two FALSIFIERs and the NULL -- so they name a path under `runs/`
in their prose and compute from the paper and from circuits they build. `e452`'s own sweep called all eight *answering;
a clone would take numbers from them*, and for these two that is wrong: what a clone takes from them is what it would
take with the corpus in place.

**And one of the eight is not measurable by this instrument.** `e200_draw_confound_audit` writes an audit with no
`claims` block in either arm, so there is no verdict of its own to compare -- which is why **RB1 fires**: the registered
claim asked every arm's artifact to carry claims, and one module's does not. It is the arm that is unshaped and not the
reading.

**And `e452`'s own vacuity is the honest kind.** Its **CY5** asks whether the corpus is over 100 MB and over 1000 files;
with the corpus it is MET and without it FALSIFIER, which is the answer the claim deserves. So of the five that move,
one moves *toward* a refusal because the question is about the corpus, and four move because a claim about the corpus
was satisfied by having none.

**And the corpus arm is exactly the gate's reading.** Seven of the eight have an artifact the gate writes for them and
all **7 of 7** reproduce it verdict for verdict, so the arm that has the corpus is the configuration the gate runs and
the difference between the columns above is the corpus and nothing else.

**And what this corrects is `e464`'s third claim.** It fired on *every corpus-dependent entry that answers is one the
static ledger calls refusal-less*, and its finding read the firing as *a refusal in the source is not a refusal* with
all eight named. The scope this unit measures is: **five** vacuous, of which one is vacuous by design, **two** that
never read the corpus, and **one** that records no verdicts at all. So the sentence survives and the list does not.

## 3. What it cannot do

- **One pair of runs each**: a module whose verdicts happen to agree on this corpus and this machine is called
  corpus-free, and a module that reads `runs/` for something no claim depends on is called the same way.
- **And the corpus arm is the repository as it stands**: it reads the whole corpus and not a fixed sample, so that arm
  is a reading of today's tree and not of a release.
- **And a verdict class is coarse**: a claim whose numbers move while its verdict does not is counted as unchanged,
  because what this unit asks is whether the answer would be different and not whether a digit in it would.
- **And no repair**: this unit says which of the eight are vacuous and changes none of them, so the four modules whose
  claims are satisfied by an empty corpus still answer a clone in the same words
  (`docs/findings/2026-10-08-the-fresh-clone-simulated.md`).
