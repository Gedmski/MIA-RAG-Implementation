# MBMIA Evaluation Protocol

This protocol is the supported path for producing publishable mask-based membership inference attack results from this repository. It is intended to address near-ceiling MBMIA results that can arise when the evaluation is mostly measuring whether a masked query retrieves an exact full document.

## Required Controls

1. Use disjoint calibration and evaluation targets.
   - Member calibration targets and member evaluation targets are sampled from the indexed corpus without overlap.
   - Non-member calibration targets and non-member evaluation targets are sampled from the held-out corpus without overlap.
   - Binary metrics use the calibration-selected threshold only; held-out evaluation scores must not tune `gamma`.

2. Keep ranking and thresholded metrics separate.
   - ROC AUC and PR-AUC use continuous mask accuracy scores.
   - Accuracy, precision, recall, F1, and balanced accuracy use the effective decision threshold.
   - `ablation_gamma` disables threshold calibration by design; all other paper-facing studies should leave it enabled.

3. Report uncertainty and low-FPR behavior.
   - Each run reports bootstrap AUC confidence intervals.
   - Each run reports TPR at 1% and 5% FPR.
   - Do not claim strong leakage from AUC alone when low-FPR TPR is weak or confidence intervals are wide.

4. Use realistic RAG indexing.
   - The current YAML configs set `chunk_chars` and `chunk_overlap` so the generator receives retrieved chunks, not necessarily the full source document.
   - Retrieval recall is computed at the parent-document level.
   - If full-document indexing is used for reproduction, label it as a reproduction or upper-bound setting.

5. Check contamination.
   - Each result row reports exact and near-duplicate non-member rates against the indexed corpus.
   - Runs with non-zero duplicate rates should be excluded or explicitly analyzed as contaminated.

6. Check mask and context leakage controls.
   - Each result row reports masked-query answer leakage, retrieved-context answer coverage, short-answer rate, and common-answer rate.
   - Any non-zero masked-query answer leakage means the probe itself contains an answer elsewhere and should be treated as invalid or analyzed separately.
   - Near-ceiling AUC with near-complete member context answer coverage should be described as retrieval-context exposure, not as unexplained model memorization.

7. Separate retrieval exposure from generator behavior.
   - `context_mode: full` measures the end-to-end RAG exposure setting.
   - `context_mode: none` measures reconstruction without retrieved context.
   - `context_mode: answer_censored` retrieves normally but replaces every masked answer in the supplied context.
   - `context_mode: leave_one_chunk_out` removes answer-bearing chunks from the target member document and refills context from the larger candidate pool.
   - Compare MBMIA AUC with `retrieval_only_auc`, which ranks examples using masked-query overlap with the retrieved text.
   - Report raw and effective context-answer coverage so censoring and chunk exclusion can be verified.

8. Use adequate sampling and independent repetitions.
   - Smoke results use only 10 evaluation examples per class and are not paper-facing estimates.
   - The publication control config uses 200 evaluation and 100 calibration examples per class with 2,000 indexed documents.
   - Average results across at least five dataset seeds; a bootstrap over one perfectly separated small sample is not a substitute for independent splits.
   - Prefer fractional masking (for example, `mask_fraction: 0.20`) so probe difficulty scales with document length.

## Recommended Paper Workflow

1. Run `python scripts/validate_mbmia_protocol.py` to confirm the protocol controls resolve correctly.
2. Run `configs/smoke.yaml` to confirm the model, dataset, retriever, and reporting environment.
3. Run `configs/lean_ablation.yaml` for the main paper tables.
4. Run `configs/publication_controls.yaml` before interpreting near-ceiling AUC as more than retrieval-context exposure.
5. Use `summary.csv` and `runs.jsonl` from a single timestamped run directory as the source of truth. `runs.jsonl` includes aggregate metrics plus per-example diagnostic scores.
6. Run `python scripts/audit_mbmia_results.py results/YYYY-MM-DD/<run_id>/summary.csv --strict` before copying numbers into the manuscript.
7. Report the effective `gamma`, `threshold_source`, context mode, calibration sample counts, chunking parameters, duplicate diagnostics, retrieval-only AUC, query leakage, and both raw and effective context-answer coverage.
8. Treat the root `experiment_results.md`, `experiment_data.csv`, and `results_report.md` as compatibility mirrors only.

## Interpretation Guardrails

- Near-ceiling AUC is not automatically invalid, but it requires evidence that the result is not caused by full-document retrieval, threshold tuning on the test set, or separable member/non-member construction.
- A gamma sweep does not change ROC AUC in principle; it changes thresholded operating-point metrics such as F1.
- Strong MBMIA results should be framed as evidence for the evaluated RAG setup and probe protocol, not as a universal claim about all LLM or RAG deployments.
