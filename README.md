# MBA RAG Package

This repository now uses a package-based layout for the Mask-Based Membership Inference Attack (MBA) workflow. The live implementation is under `src/mia_rag`, YAML configs under `configs/`, and canonical run artifacts under `results/YYYY-MM-DD/<run_id>/`.

## Live Structure

- `src/mia_rag`: config loading, dataset loaders, masking, RAG pipeline, experiment runner, reporting, and legacy compatibility helpers
- `configs/default.yaml`: legacy full experiment sweep across baseline and new datasets
- `configs/smoke.yaml`: small legacy sweep for validation in a separate VM
- `configs/lean_ablation.yaml`: study-driven lean ablation plan with shared defaults and named study blocks
- `docs/MBMIA_EVALUATION_PROTOCOL.md`: publication-oriented controls for mask-based MIA evaluation
- `results/`: canonical structured outputs for each invocation
- `mia_rag_attack.py`: compatibility wrapper for `python mia_rag_attack.py --config <yaml>`
- `process_results.py`: compatibility wrapper for `python process_results.py --input <run_dir or file>`

`archives/`, `scripts-deprecated/`, and the notebook are preserved as historical artifacts and are not part of the supported runtime surface.

## Installation

```bash
pip install -r requirements.txt
```

Ollama must be running locally for experiment execution:

```bash
ollama pull llama3
ollama pull llama3.1:8b
ollama pull llama3.1:70b
ollama pull mistral
ollama pull phi3
ollama serve
```

To run OpenAI-backed study configs such as `gpt-4o-mini`, set `OPENAI_API_KEY` in the environment before execution.

## Running Experiments

Use YAML as the primary interface. The default config enables the baseline datasets plus FiQA and ArXiv.

```bash
python mia_rag_attack.py --config configs/default.yaml
```

For a lighter validation sweep:

```bash
python mia_rag_attack.py --config configs/smoke.yaml
```

For the study-driven lean ablation layout:

```bash
python mia_rag_attack.py --config configs/lean_ablation.yaml
```

The current lean ablation config includes:

- `ablation_model_family`
- `ablation_model_scale`
- `ablation_mask_count`
- `ablation_gamma`
- `ablation_retrieval_depth`
- `ablation_retrieval_stack`
- `ablation_domain_stack_control`
- `robustness_cross_dataset`
- `optional_scale_study`

The current configs use the journal-oriented MBMIA controls by default:

- disjoint calibration and held-out evaluation targets
- calibration-only threshold selection for binary F1/accuracy metrics
- ROC AUC, PR-AUC, balanced accuracy, and low-FPR TPR reporting
- bootstrap AUC confidence intervals
- chunked RAG indexing with parent-document retrieval-hit diagnostics
- exact and near-duplicate checks for non-member contamination
- masked-query answer leakage and retrieved-context answer coverage diagnostics

The `ablation_gamma` study intentionally disables threshold calibration so it can measure fixed-threshold sensitivity. Other studies should normally keep calibration enabled.

Before running model-backed studies, validate the protocol wiring:

```bash
python scripts/validate_mbmia_protocol.py
```

Before using a result table in the manuscript, audit it for missing controls:

```bash
python scripts/audit_mbmia_results.py results/YYYY-MM-DD/<run_id>/summary.csv --strict
```

Each run writes:

- `resolved_config.yaml`
- `runs.jsonl`
- `failures.jsonl`
- `summary.csv`
- `report.md`
- `plots/`

Study-driven configs also write per-study outputs under `studies/<study_name>/` inside the main run directory, with a combined top-level summary for the invocation.

The latest structured results are also mirrored to the root compatibility files:

- `experiment_results.md`
- `experiment_data.csv`
- `results_report.md`

Historical March/April result files in this repository were produced before the calibrated/chunked protocol. Treat their near-ceiling MBMIA AUC values as reproduction artifacts, not journal-ready evidence, until the studies are rerun with the current configs.

## Processing Results

Process a structured run directory:

```bash
python process_results.py --input results/2026-03-28/120000
```

Process a structured JSONL file:

```bash
python process_results.py --input results/2026-03-28/120000/runs.jsonl
```

Process a legacy markdown log:

```bash
python process_results.py --input experiment_results.md
```

## YAML Contract

Every config file must include these top-level sections:

- `paths`
- `datasets`
- `models`
- `retrievers`
- `embeddings`
- `runtime`
- `reporting`

And then either:

- `sweeps` for the legacy Cartesian-sweep mode
- `defaults` and `studies` for the lean study-driven mode

Each dataset entry defines its loader, source dataset, sizing rules, and normalization constraints. `MIAConfig` is now a resolved single-run type generated from either the legacy sweep expansion or the study-driven resolver rather than something edited manually in a script.

In study-driven mode:

- `defaults` pins the shared baseline configuration
- each `studies.<name>.overrides` block changes fixed values for that study
- each `studies.<name>.sweep` block varies only the factors named in that study
- supported study fields are `dataset`, `model`, `retriever`, `embedding`, `num_masks`, `retriever_k`, `gamma`, `index_size`, `eval_size`, and `seed`
- publication-control fields are also supported: `calibration_size`, `calibrate_threshold`, `bootstrap_iterations`, `chunk_chars`, and `chunk_overlap`

Optional model metadata keys are also supported in the `models` section:

- `family`
- `size_label`
- `params_b`
- `closed_weights`

## Dataset Defaults

The current packaged loaders cover:

- `healthcaremagic`
- `msmarco`
- `nq`
- `fiqa`
- `arxiv`

Default new dataset sources:

- FiQA via [BeIR/fiqa](https://huggingface.co/datasets/BeIR/fiqa)
- ArXiv abstracts via [MaartenGr/arxiv_nlp](https://huggingface.co/datasets/MaartenGr/arxiv_nlp)

These defaults can be overridden in YAML without changing the codebase.
