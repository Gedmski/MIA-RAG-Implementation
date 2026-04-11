from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mia_rag.types import DocumentRecord
from mia_rag import runner


class FakeLoader:
    def __init__(self):
        self.calls: list[tuple[int, int, int | None]] = []

    def load_documents(self, spec):
        self.calls.append((spec.index_size, spec.eval_size, spec.seed))
        required = spec.index_size + spec.eval_size
        return [
            DocumentRecord(
                doc_id=str(index),
                text=f"Document {index} " * 40,
                metadata={},
            )
            for index in range(required)
        ]


def test_run_experiments_writes_per_study_outputs_and_reuses_cache(tmp_path, monkeypatch):
    config_path = tmp_path / "study-runner.yaml"
    results_root = tmp_path / "results"
    config_path.write_text(
        f"""
paths:
  results_root: {results_root.as_posix()}
  legacy_experiment_log: legacy.md
  legacy_csv: legacy.csv
  legacy_report: legacy-report.md
datasets:
  sample:
    loader: healthcaremagic
    enabled: true
    dataset_id: sample-dataset
    split: train
    index_size: 10
    eval_size: 2
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
  gamma: 0.5
studies:
  baseline:
    overrides: {{}}
    sweep: {{}}
  scale:
    overrides: {{}}
    sweep:
      index_size:
        - 10
        - 20
""",
        encoding="utf-8",
    )

    fake_loader = FakeLoader()
    monkeypatch.setattr(runner, "get_dataset_loader", lambda _: fake_loader)

    def fake_run_single_experiment(config, split):
        return {
            "study_name": config.study_name,
            "status": "success",
            "dataset": config.dataset_name,
            "dataset_loader": config.dataset_loader,
            "model_provider": config.model_provider,
            "llm_model": config.llm_model,
            "llm_model_name": config.llm_model_name,
            "model_family": config.model_family,
            "model_size_label": config.model_size_label,
            "model_params_b": config.model_params_b,
            "closed_weights": config.closed_weights,
            "embedding_model": config.embedding_model,
            "embedding_model_name": config.embedding_model_name,
            "retriever_type": config.retriever_type,
            "num_masks": config.num_masks,
            "retriever_k": config.retriever_k,
            "gamma": config.gamma,
            "index_size": config.index_size,
            "eval_size": config.eval_size,
            "member_samples": len(split.eval_members),
            "non_member_samples": len(split.eval_non_members),
            "auc": 0.95,
            "accuracy": 0.90,
            "precision": 0.92,
            "recall": 0.88,
            "f1": 0.90,
            "retrieval_recall": 1.0,
            "member_mean_mask_accuracy": 0.85,
            "non_member_mean_mask_accuracy": 0.15,
            "member_mean_format_coverage": 0.90,
            "non_member_mean_format_coverage": 0.35,
            "member_exact_reconstruction_rate": 0.60,
            "non_member_exact_reconstruction_rate": 0.05,
            "generation_failure_rate": 0.40,
            "runtime_seconds": 0.1,
            "failure_reason": "",
            "config_repr": config.compat_repr(),
        }

    monkeypatch.setattr(runner, "run_single_experiment", fake_run_single_experiment)

    run_dir = runner.run_experiments(config_path)
    assert (run_dir / "summary.csv").exists()
    assert (run_dir / "studies" / "baseline" / "summary.csv").exists()
    assert (run_dir / "studies" / "scale" / "summary.csv").exists()

    assert fake_loader.calls == [(10, 2, 42), (20, 2, 42)]

    lines = (run_dir / "runs.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 3
    first_record = json.loads(lines[0])
    assert first_record["study_name"] in {"baseline", "scale"}
    assert "gamma" in first_record
    assert "generation_failure_rate" in first_record
