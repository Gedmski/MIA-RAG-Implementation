# MBA RAG Package

This repository now uses a package-based layout for the Mask-Based Membership Inference Attack (MBA) workflow. The live implementation is under `src/mia_rag`, YAML configs under `configs/`, and canonical run artifacts under `results/YYYY-MM-DD/<run_id>/`.

## Live Structure

- `src/mia_rag`: config loading, dataset loaders, masking, RAG pipeline, experiment runner, reporting, and legacy compatibility helpers
- `configs/default.yaml`: legacy full experiment sweep across baseline and new datasets
- `configs/smoke.yaml`: small legacy sweep for validation in a separate VM
- `configs/lean_ablation.yaml`: study-driven lean ablation plan with shared defaults and named study blocks
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
