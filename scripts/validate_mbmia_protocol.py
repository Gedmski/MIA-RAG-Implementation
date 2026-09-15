from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mia_rag.config import expand_experiment_configs, expand_experiment_studies, load_experiment_spec
from mia_rag.datasets import prepare_dataset_split
from mia_rag.pipeline import (
    _answer_occurrence_counts,
    _is_non_leaking_mask_candidate,
    bootstrap_auc_ci,
    chunk_document_text,
    compute_membership_metrics,
    evaluate_mask_quality,
    evaluate_reconstruction,
    redact_answers_from_context,
    retrieval_overlap_score,
    select_context_documents,
    select_decision_threshold,
)
from mia_rag.types import DocumentRecord


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _validate_configs() -> None:
    expected = {
        "configs/smoke.yaml": (5, 500, True, True),
        "configs/lean_ablation.yaml": (25, 800, True, True),
        "configs/default.yaml": (25, 800, True, True),
        "configs/publication_controls.yaml": (100, 500, True, True),
    }
    for config_name, (calibration_size, chunk_chars, calibrate_threshold, avoid_leakage) in expected.items():
        spec = load_experiment_spec(ROOT / config_name)
        configs = expand_experiment_configs(spec)
        _assert(configs, f"{config_name} produced no resolved configs")
        first = configs[0]
        _assert(first.calibration_size == calibration_size, f"{config_name} calibration_size mismatch")
        _assert(first.chunk_chars == chunk_chars, f"{config_name} chunk_chars mismatch")
        _assert(first.calibrate_threshold is calibrate_threshold, f"{config_name} calibration flag mismatch")
        _assert(first.avoid_query_answer_leakage is avoid_leakage, f"{config_name} leakage-prevention flag mismatch")
        _assert(first.context_mode in {"full", "none", "answer_censored", "leave_one_chunk_out"}, f"{config_name} context mode mismatch")

    lean_spec = load_experiment_spec(ROOT / "configs/lean_ablation.yaml")
    studies = {study.name: study for study in expand_experiment_studies(lean_spec)}
    _assert(studies["baseline_reproduction"].configs[0].calibrate_threshold is True, "baseline must calibrate")
    _assert(studies["ablation_gamma"].configs[0].calibrate_threshold is False, "gamma study must be fixed-threshold")

    publication_spec = load_experiment_spec(ROOT / "configs/publication_controls.yaml")
    publication_configs = expand_experiment_configs(publication_spec)
    _assert(len(publication_configs) == 40, "publication context study must resolve 40 runs")
    _assert({config.seed for config in publication_configs} == {42, 1337, 2027, 31415, 65537}, "publication seeds mismatch")


def _validate_splits() -> None:
    documents = [
        DocumentRecord(doc_id=str(index), text=(f"Document {index:03d} " * 40), metadata={})
        for index in range(30)
    ]
    split = prepare_dataset_split(documents, index_size=12, eval_size=4, calibration_size=3, seed=7)
    _assert(len(split.calibration_members) == 3, "member calibration size mismatch")
    _assert(len(split.eval_members) == 4, "member eval size mismatch")
    _assert(len(split.calibration_non_members) == 3, "non-member calibration size mismatch")
    _assert(len(split.eval_non_members) == 4, "non-member eval size mismatch")
    calibration_ids = {document.doc_id for document in split.calibration_members}
    eval_ids = {document.doc_id for document in split.eval_members}
    _assert(calibration_ids.isdisjoint(eval_ids), "member calibration/eval targets overlap")


def _validate_metrics() -> None:
    metrics = compute_membership_metrics([1, 1, 0, 0], [0.9, 0.6, 0.7, 0.1], gamma=0.7)
    _assert(round(metrics["auc"], 4) == 0.75, "AUC calculation changed unexpectedly")
    _assert("pr_auc" in metrics, "PR-AUC missing")
    _assert("tpr_at_5_fpr" in metrics, "low-FPR TPR missing")

    threshold = select_decision_threshold([1, 1, 0, 0], [0.8, 0.7, 0.4, 0.2], fallback_gamma=0.1)
    _assert(threshold == 0.7, "calibration threshold selection changed unexpectedly")

    ci_low, ci_high = bootstrap_auc_ci([1, 1, 0, 0], [0.9, 0.6, 0.7, 0.1], iterations=20, seed=42)
    _assert(ci_low is not None and ci_high is not None, "bootstrap CI missing")


def _validate_scoring_and_chunking() -> None:
    chunks = chunk_document_text("abcdefghijklmnopqrstuvwxyz", chunk_chars=10, chunk_overlap=2)
    _assert(chunks == ["abcdefghij", "ijklmnopqr", "qrstuvwxyz"], "chunk overlap behavior changed")

    diagnostics = evaluate_reconstruction("[MASK_1]: insulinized", {"[MASK_1]": ["insulin"]})
    _assert(diagnostics.mask_accuracy == 0.0, "substring answer was counted as exact reconstruction")

    mask_quality = evaluate_mask_quality(
        masked_text="The [MASK_1] dose lowered insulin levels.",
        ground_truth={"[MASK_1]": ["insulin"]},
        retrieved_context="The patient was prescribed insulin.",
    )
    _assert(mask_quality.query_answer_leakage == 1.0, "masked-query answer leakage was not detected")
    _assert(mask_quality.context_answer_coverage == 1.0, "retrieved-context answer coverage was not detected")

    counts = _answer_occurrence_counts("insulin lowers glucose but insulin can vary".split())
    _assert(_is_non_leaking_mask_candidate("glucose", counts), "unique answer was rejected")
    _assert(not _is_non_leaking_mask_candidate("insulin", counts), "repeated answer was accepted")

    redacted = redact_answers_from_context(
        "The patient takes insulin daily.",
        {"[MASK_1]": ["insulin"]},
    )
    _assert("insulin" not in redacted.lower(), "answer-censored context still contains the answer")

    class Candidate:
        def __init__(self, text: str, parent_id: str):
            self.page_content = text
            self.metadata = {"parent_id": parent_id}

    candidates = [
        Candidate("The insulin dose changed.", "member-1"),
        Candidate("Follow-up is scheduled tomorrow.", "member-1"),
        Candidate("An unrelated clinical note.", "member-2"),
    ]
    selected = select_context_documents(
        candidates,
        context_mode="leave_one_chunk_out",
        retriever_k=2,
        target_doc_id="member-1",
        ground_truth={"[MASK_1]": ["insulin"]},
    )
    _assert(len(selected) == 2 and "insulin" not in selected[0].page_content.lower(), "answer chunk exclusion failed")
    _assert(retrieval_overlap_score("The [MASK_1] dose changed.", candidates) > 0.0, "retrieval-only score missing")


def main() -> int:
    _validate_configs()
    _validate_splits()
    _validate_metrics()
    _validate_scoring_and_chunking()
    print("MBMIA protocol validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
