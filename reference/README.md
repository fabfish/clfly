# `reference/lgcl_source/` — provenance

These files are **not part of the clfly package**. They are the source materials
this project builds on, included so the reproduction in `clfly/lgcl/repro.py` can
be checked against the originals rather than against a summary.

Provided as a zip attachment alongside `EWC λ与模型建议.docx`.

## Contents

| File | What it is |
|---|---|
| `LGCL技术备忘录.md` | technical memo — model definition, the correspondence table, findings 1–4, theorem roadmap, and the "immediately actionable" recommendations for the field |
| `LGCL论文初稿v2.md` … `v8_*.md` | successive manuscript drafts; v5 quantifies the replay recovery curve, v6 proves Theorem B, v7 is the MNIST-level benchmark validation, v8 adds the analytic replay recovery and the Gram-basis re-test |
| `lgcl_toy.py` | the original experiment script — **the** reference implementation for `clfly/lgcl/` |
| `lgcl_results.json` | every published Monte Carlo number |
| `fig1`–`fig14` | published figures |
| `相关工作调研_可解模型与贝叶斯视角.md` | literature positioning memo, including the six-claim novelty assessment against the closest prior work |

## How clfly uses them

`clfly/lgcl/repro.py` recomputes the numbers in `lgcl_results.json` and gates on
the worst deviation. Which anchors are allowed to gate is decided by whether the
materials pin down the generating configuration — see the module docstring and
`docs/findings/2026-09-20-phase1-lgcl-port.md` §2.

`EXP1_*` reproduces to 4.7e-5. The `exp3`/`exp4`/`exp5` families do not, because
`lgcl_toy.py` contains only helpers for them — the driver scripts were not
included, so the configurations are unrecoverable. They are quarantined under
`--explore`.
