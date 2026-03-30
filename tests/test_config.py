from __future__ import annotations

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mia_rag.config import expand_experiment_configs, expand_experiment_studies, load_experiment_spec


def test_load_experiment_spec_and_expand_smoke_config():
    spec = load_experiment_spec(ROOT / "configs" / "smoke.yaml")
    assert spec.paths.results_root == "results"
    assert len(spec.datasets) == 3
    healthcaremagic = next(dataset for dataset in spec.datasets if dataset.name == "healthcaremagic")
    arxiv = next(dataset for dataset in spec.datasets if dataset.name == "arxiv")
    assert healthcaremagic.loader_options["text_fields"] == ["text"]
    assert arxiv.loader_options["title_fields"] == ["Titles"]
    assert arxiv.loader_options["abstract_fields"] == ["Abstracts"]
    assert arxiv.loader_options["category_fields"] == ["Categories"]
    assert arxiv.category == "Computation and Language"
    configs = expand_experiment_configs(spec)
    assert len(configs) == 6
    first = configs[0]
    assert first.study_name == "default_sweep"
    assert first.dataset_name in {"healthcaremagic", "fiqa", "arxiv"}
    assert first.num_masks in {3, 5}
    assert first.retriever_k in {1, 3}
    assert first.gamma == 0.5


def test_study_config_expands_per_study_without_global_cross_product(tmp_path):
    config_path = tmp_path / "studies.yaml"
    config_path.write_text(
        """
paths:
  results_root: results
datasets:
  sample:
    loader: healthcaremagic
    enabled: true
    dataset_id: sample-dataset
    split: train
    index_size: 20
    eval_size: 5
models:
  gpt-4o-mini:
    provider: openai
    model_name: gpt-4o-mini
  llama3:
    provider: ollama
    model_name: llama3
retrievers:
  faiss:
    enabled: true
embeddings:
  bge:
    model_name: BAAI/bge-small-en-v1.5
runtime:
  proxy_model: gpt2
  masking_strategy: hard
  use_spelling_correction: true
  seed: 42
  gamma: 0.5
  continue_on_error: true
  limit_runs:
  llm_temperature: 0.0
reporting:
  generate_plots: false
  copy_legacy_outputs: false
defaults:
  dataset: sample
  model: gpt-4o-mini
  retriever: faiss
  embedding: bge
  num_masks: 10
  retriever_k: 5
  gamma: 0.5
studies:
  baseline:
    description: Single run
    overrides: {}
    sweep: {}
  model_gamma:
    description: Vary model and gamma only
    overrides: {}
    sweep:
      model:
        - gpt-4o-mini
        - llama3
      gamma:
        - 0.5
        - 0.7
""",
        encoding="utf-8",
    )

    spec = load_experiment_spec(config_path)
    studies = expand_experiment_studies(spec)
    assert [study.name for study in studies] == ["baseline", "model_gamma"]
    assert [len(study.configs) for study in studies] == [1, 4]

    baseline = studies[0].configs[0]
    assert baseline.llm_model == "gpt-4o-mini"
    assert baseline.llm_model_name == "gpt-4o-mini"
    assert baseline.embedding_model == "bge"
    assert baseline.embedding_model_name == "BAAI/bge-small-en-v1.5"

    expanded = expand_experiment_configs(spec)
    assert len(expanded) == 5


def test_unknown_study_model_alias_raises_clear_error(tmp_path):
    config_path = tmp_path / "bad-study.yaml"
    config_path.write_text(
        """
paths:
  results_root: results
datasets:
  sample:
    loader: healthcaremagic
    enabled: true
    dataset_id: sample-dataset
    split: train
models:
  llama3:
    provider: ollama
    model_name: llama3
retrievers:
  faiss:
    enabled: true
embeddings:
  mini:
    model_name: sentence-transformers/all-MiniLM-L6-v2
runtime:
  proxy_model: gpt2
  masking_strategy: hard
  use_spelling_correction: true
  seed: 42
  gamma: 0.5
  continue_on_error: true
  limit_runs:
  llm_temperature: 0.0
reporting:
  generate_plots: false
  copy_legacy_outputs: false
defaults:
  dataset: sample
  model: llama3
  retriever: faiss
  embedding: mini
  num_masks: 5
  retriever_k: 3
studies:
  bad_model:
    overrides: {}
    sweep:
      model:
        - missing-model
""",
        encoding="utf-8",
    )

    spec = load_experiment_spec(config_path)
    with pytest.raises(ValueError, match="Unknown model"):
        expand_experiment_configs(spec)


def test_model_registry_requires_provider_metadata(tmp_path):
    config_path = tmp_path / "bad-models.yaml"
    config_path.write_text(
        """
paths:
  results_root: results
datasets:
  - name: sample
    loader: healthcaremagic
    enabled: true
    dataset_id: sample-dataset
    split: train
models:
  llama3:
    model_name: llama3
retrievers:
  - faiss
embeddings:
  - sentence-transformers/all-MiniLM-L6-v2
studies:
  baseline:
    overrides:
      dataset: sample
      model: llama3
      retriever: faiss
      embedding: sentence-transformers/all-MiniLM-L6-v2
      num_masks: 5
      retriever_k: 3
    sweep: {}
runtime:
  proxy_model: gpt2
  masking_strategy: hard
  use_spelling_correction: true
  seed: 42
  gamma: 0.5
  continue_on_error: true
  limit_runs:
  llm_temperature: 0.0
reporting:
  generate_plots: false
  copy_legacy_outputs: false
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing required 'provider' metadata"):
        load_experiment_spec(config_path)
