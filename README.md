# MBA RAG Package

This repository now uses a package-based layout for the Mask-Based Membership Inference Attack (MBA) workflow. The live implementation is under `src/mia_rag`, YAML configs under `configs/`, and canonical run artifacts under `results/YYYY-MM-DD/<run_id>/`.

## Live Structure

- `src/mia_rag`: config loading, dataset loaders, masking, RAG pipeline, experiment runner, reporting, and legacy compatibility helpers
- `configs/default.yaml`: full experiment sweep across baseline and new datasets
- `configs/smoke.yaml`: small sweep for validation in a separate VM
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

## Running Experiments

Use YAML as the primary interface. The default config enables the baseline datasets plus FiQA and ArXiv.

```bash
python mia_rag_attack.py --config configs/default.yaml
```

For a lighter validation sweep:

```bash
python mia_rag_attack.py --config configs/smoke.yaml
```

Each run writes:

- `resolved_config.yaml`
- `runs.jsonl`
- `failures.jsonl`
- `summary.csv`
- `report.md`
- `plots/`

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
- `sweeps`
- `runtime`
- `reporting`

Each dataset entry defines its loader, source dataset, sizing rules, and normalization constraints. `MIAConfig` is now a resolved single-run type generated from the YAML sweep expansion rather than something edited manually in a script.

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
