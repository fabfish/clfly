"""`e185` checks the plan's benchmark block against the code, and every arm of it was bought with a false positive.

The block is prose, so the check needed a contract before it could say anything: two marked lists (implemented,
proposed) and one for the baselines. Building that contract produced four errors worth pinning here, because they
are the shape this kind of check fails in:

- the section's **heading** terminated the first list, so the implemented suite read as empty and all three tasks
  were flagged -- a check that reported the code's own suite as missing from a block that names it;
- the list collector ran to the end of the block, so the baseline check read **prose** and flagged `e185` (the
  checker's own name), `clfly/bench/` (the reference framework) and the three baselines the block says are *not*
  implemented;
- the mark's own line was scanned, which flagged `e185` a second way;
- and a `{column=prefix}` written in the block's own *explanation* of the probe syntax was read as a probe.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e185_benchmark_spec_audit as e185

SPECS = (("odour_identity", ("cell_type", ("KC",)), ("cell_class", ("MBON",))),
         ("heading", ("cell_type", ("EPG",)), ("cell_class", ("CX",))))

HEAD = "# plan\n\n"
FOOT = "\n## Experimental programme\n\nnothing here\n"


def build(tmp_path: Path, block: str, artifacts: dict[str, dict] | None = None) -> tuple[Path, Path]:
    """A synthetic plan and runs dir. The default artifact is what makes the block's `naive` baseline real: the
    baseline arm is evidence-backed by the corpus, so a block offering `naive` with no run of it is a flag."""
    plan = tmp_path / "plan.md"
    plan.parent.mkdir(parents=True, exist_ok=True)
    plan.write_text(HEAD + block + FOOT, encoding="utf-8")
    runs = tmp_path / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    for name, cfg in ({"e9_a.json": {"methods": "naive"}} if artifacts is None else artifacts).items():
        (runs / name).write_text(json.dumps({"config": cfg}), encoding="utf-8")
    return plan, runs


BLOCK = ("## The benchmark — FlyCL v0\n\n"
         "**Implemented suite (checked by `e185`):**\n\n"
         "1. olfaction (`odour_identity`)\n2. heading (`heading`)\n\n"
         "**Proposed and not implemented (checked by `e185`):**\n\n"
         "1. visual motion — `{cell_type=T4}`\n\n"
         "**Baselines (checked by `e185`):**\n\n- `naive` — run\n- `oracle` — the reference line\n\n"
         "Metrics: nothing to check here.\n")


def test_a_matching_block_passes_and_a_missing_task_is_flagged(tmp_path):
    plan, runs = build(tmp_path, BLOCK)
    res = e185.audit(plan, runs, specs=SPECS)
    assert res["n_flags"] == 0, res["flags"]
    plan2, runs2 = build(tmp_path / "b", BLOCK.replace("1. olfaction (`odour_identity`)\n", ""))
    res2 = e185.audit(plan2, runs2, specs=SPECS)
    assert [f["token"] for f in res2["flags"]] == ["odour_identity"]


def test_the_heading_does_not_terminate_the_first_list(tmp_path):
    """The failure that made the check report the code's own suite as absent from the block that names it."""
    plan, _ = build(tmp_path, BLOCK)
    assert "odour_identity" in e185.tokens(e185.marked(
        e185.benchmark_block(plan.read_text(encoding="utf-8")).splitlines(), e185.IMPLEMENTED_MARK))


def test_a_task_the_block_calls_unimplemented_and_the_code_builds_is_flagged(tmp_path):
    plan, runs = build(tmp_path, BLOCK.replace("1. visual motion — `{cell_type=T4}`",
                                               "1. heading again (`heading`)"))
    res = e185.audit(plan, runs, specs=SPECS)
    assert [f["what"] for f in res["flags"]] == ["the proposed list names a task the code builds"]


def test_the_baseline_check_reads_the_list_and_not_the_prose(tmp_path):
    """It flagged `e185`, `clfly/bench/` and the block's own statement that `SI` is NOT implemented."""
    plan, runs = build(tmp_path, BLOCK + "\n**SI and MAS appear nowhere and have never been run.**\n")
    assert e185.audit(plan, runs, specs=SPECS)["n_flags"] == 0
    plan2, runs2 = build(tmp_path / "b",
                         BLOCK.replace("- `oracle` — the reference line", "- `MAS` — offered, supposedly"))
    flags = e185.audit(plan2, runs2, specs=SPECS)["flags"]
    assert [f["token"] for f in flags] == ["MAS"]


def test_a_baseline_is_evidence_backed_by_the_corpus_not_by_a_word_list(tmp_path):
    """`naive` counts because a run has it in `config.methods`; with no such artifact it is flagged."""
    plan, runs = build(tmp_path, BLOCK, {})
    assert [f["token"] for f in e185.audit(plan, runs, specs=SPECS)["flags"]] == ["naive"]


def test_the_probe_syntax_in_the_block_s_explanation_is_not_read_as_a_probe(tmp_path):
    plan, runs = build(tmp_path, BLOCK + "the check reads a brace group holding `column=prefix`.\n")
    assert e185.audit(plan, runs, specs=SPECS)["probes"] == ["cell_type=T4"]


def test_the_live_block_passes_against_the_code_and_the_corpus():
    """The gate. `--populations` is not run here: it loads the connectome, and the text and corpus arms are the
    ones that can drift when a task or a method is added."""
    res = e185.audit(Path("docs/research_plan.md"), Path("runs"))
    assert res["n_flags"] == 0, res["flags"]
    assert set(res["specs"]) == {"odour_identity", "heading", "odour_input"}
    assert {"naive", "ewc", "replay"} <= set(res["methods_the_corpus_ran"])
    assert len(res["probes"]) >= 5, "the block must keep naming the populations of its proposed modalities"
