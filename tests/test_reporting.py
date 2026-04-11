from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mia_rag.legacy import parse_legacy_markdown
from mia_rag.reporting import generate_report, load_structured_records, write_structured_records


def _sample_records():
    return [
        {
            "study_name": "baseline_reproduction",
            "run_name": "baseline-healthcaremagic-llama3-faiss-mini-m5-k3",
            "started_at": "2026-03-28 12:00:00",
            "finished_at": "2026-03-28 12:10:00",
            "status": "success",
            "dataset": "healthcaremagic",
            "dataset_loader": "healthcaremagic",
            "model_provider": "ollama",
            "llm_model": "llama3",
            "llm_model_name": "llama3",
            "model_family": "llama3",
            "model_size_label": "default",
            "model_params_b": None,
            "closed_weights": False,
            "embedding_model": "all-minilm-l6-v2",
            "embedding_model_name": "sentence-transformers/all-MiniLM-L6-v2",
            "retriever_type": "faiss",
            "num_masks": 5,
            "retriever_k": 3,
            "gamma": 0.5,
            "index_size": 500,
            "eval_size": 50,
            "member_samples": 50,
            "non_member_samples": 50,
            "auc": 0.95,
            "accuracy": 0.90,
            "precision": 0.92,
            "recall": 0.88,
            "f1": 0.90,
            "retrieval_recall": 1.0,
            "member_mean_mask_accuracy": 0.88,
            "non_member_mean_mask_accuracy": 0.12,
            "member_mean_format_coverage": 0.90,
            "non_member_mean_format_coverage": 0.30,
            "member_exact_reconstruction_rate": 0.52,
            "non_member_exact_reconstruction_rate": 0.04,
            "generation_failure_rate": 0.22,
            "runtime_seconds": 42.0,
            "failure_reason": "",
            "config_repr": "Config(...)",
        },
        {
            "study_name": "ablation_gamma",
            "run_name": "gamma-healthcaremagic-gpt-faiss-bge-m10-k5",
            "started_at": "2026-03-28 13:00:00",
            "finished_at": "2026-03-28 13:08:00",
            "status": "success",
            "dataset": "healthcaremagic",
            "dataset_loader": "healthcaremagic",
            "model_provider": "openai",
            "llm_model": "gpt-4o-mini",
            "llm_model_name": "gpt-4o-mini",
            "model_family": "gpt-4o",
            "model_size_label": "mini",
            "model_params_b": None,
            "closed_weights": True,
            "embedding_model": "bge-small-en-v1.5",
            "embedding_model_name": "BAAI/bge-small-en-v1.5",
            "retriever_type": "faiss",
            "num_masks": 10,
            "retriever_k": 5,
            "gamma": 0.7,
            "index_size": 500,
            "eval_size": 50,
            "member_samples": 50,
            "non_member_samples": 50,
            "auc": 0.97,
            "accuracy": 0.91,
            "precision": 0.93,
            "recall": 0.90,
            "f1": 0.91,
            "retrieval_recall": 0.99,
            "member_mean_mask_accuracy": 0.91,
            "non_member_mean_mask_accuracy": 0.18,
            "member_mean_format_coverage": 0.95,
            "non_member_mean_format_coverage": 0.32,
            "member_exact_reconstruction_rate": 0.61,
            "non_member_exact_reconstruction_rate": 0.06,
            "generation_failure_rate": 0.18,
            "runtime_seconds": 50.0,
            "failure_reason": "",
            "config_repr": "Config(...)",
        },
        {
            "study_name": "ablation_gamma",
            "run_name": "gamma-fiqa-gpt-faiss-bge-m10-k5",
            "started_at": "2026-03-28 14:00:00",
            "finished_at": "2026-03-28 14:08:00",
            "status": "failed",
            "dataset": "fiqa",
            "dataset_loader": "fiqa",
            "model_provider": "openai",
            "llm_model": "gpt-4o-mini",
            "llm_model_name": "gpt-4o-mini",
            "model_family": "gpt-4o",
            "model_size_label": "mini",
            "model_params_b": None,
            "closed_weights": True,
            "embedding_model": "bge-small-en-v1.5",
            "embedding_model_name": "BAAI/bge-small-en-v1.5",
            "retriever_type": "faiss",
            "num_masks": 10,
            "retriever_k": 5,
            "gamma": 0.7,
            "index_size": 500,
            "eval_size": 50,
            "member_samples": 0,
            "non_member_samples": 0,
            "auc": None,
            "accuracy": None,
            "precision": None,
            "recall": None,
            "f1": None,
            "retrieval_recall": None,
            "member_mean_mask_accuracy": None,
            "non_member_mean_mask_accuracy": None,
            "member_mean_format_coverage": None,
            "non_member_mean_format_coverage": None,
            "member_exact_reconstruction_rate": None,
            "non_member_exact_reconstruction_rate": None,
            "generation_failure_rate": None,
            "runtime_seconds": 3.0,
            "failure_reason": "dataset load failed",
            "config_repr": "Config(...)",
        },
    ]


def test_reporting_round_trip(tmp_path):
    records = _sample_records()
    runs_path = tmp_path / "runs.jsonl"
    write_structured_records(records, runs_path)
    dataframe = load_structured_records(runs_path)
    assert len(dataframe) == 3
    assert "study_name" in dataframe.columns
    assert "f1" in dataframe.columns
    assert "generation_failure_rate" in dataframe.columns

    report_path = tmp_path / "report.md"
    generate_report(dataframe, report_path)
    report_text = report_path.read_text(encoding="utf-8")
    assert "Study Overview" in report_text
    assert "Dataset: healthcaremagic" in report_text
    assert "Best F1" in report_text


def test_reporting_adds_model_scale_and_domain_control_sections(tmp_path):
    records = [
        {
            "study_name": "ablation_model_scale",
            "run_name": "scale-healthcaremagic-gpt-4o-mini",
            "started_at": "2026-03-28 12:00:00",
            "finished_at": "2026-03-28 12:10:00",
            "status": "success",
            "dataset": "healthcaremagic",
            "dataset_loader": "healthcaremagic",
            "model_provider": "openai",
            "llm_model": "gpt-4o-mini",
            "llm_model_name": "gpt-4o-mini",
            "model_family": "gpt-4o",
            "model_size_label": "mini",
            "model_params_b": None,
            "closed_weights": True,
            "embedding_model": "bge-small-en-v1.5",
            "embedding_model_name": "BAAI/bge-small-en-v1.5",
            "retriever_type": "faiss",
            "num_masks": 10,
            "retriever_k": 5,
            "gamma": 0.5,
            "index_size": 500,
            "eval_size": 50,
            "member_samples": 50,
            "non_member_samples": 50,
            "auc": 0.99,
            "accuracy": 0.90,
            "precision": 0.92,
            "recall": 0.88,
            "f1": 0.90,
            "retrieval_recall": 1.0,
            "member_mean_mask_accuracy": 0.90,
            "non_member_mean_mask_accuracy": 0.12,
            "member_mean_format_coverage": 0.95,
            "non_member_mean_format_coverage": 0.35,
            "member_exact_reconstruction_rate": 0.60,
            "non_member_exact_reconstruction_rate": 0.02,
            "generation_failure_rate": 0.20,
            "runtime_seconds": 10.0,
            "failure_reason": "",
            "config_repr": "Config(...)",
        },
        {
            "study_name": "ablation_model_scale",
            "run_name": "scale-healthcaremagic-llama3.1-70b",
            "started_at": "2026-03-28 12:11:00",
            "finished_at": "2026-03-28 12:21:00",
            "status": "success",
            "dataset": "healthcaremagic",
            "dataset_loader": "healthcaremagic",
            "model_provider": "ollama",
            "llm_model": "llama3.1-70b",
            "llm_model_name": "llama3.1:70b",
            "model_family": "llama3.1",
            "model_size_label": "70B",
            "model_params_b": 70.0,
            "closed_weights": False,
            "embedding_model": "bge-small-en-v1.5",
            "embedding_model_name": "BAAI/bge-small-en-v1.5",
            "retriever_type": "faiss",
            "num_masks": 10,
            "retriever_k": 5,
            "gamma": 0.5,
            "index_size": 500,
            "eval_size": 50,
            "member_samples": 50,
            "non_member_samples": 50,
            "auc": 0.995,
            "accuracy": 0.93,
            "precision": 0.95,
            "recall": 0.90,
            "f1": 0.92,
            "retrieval_recall": 1.0,
            "member_mean_mask_accuracy": 0.93,
            "non_member_mean_mask_accuracy": 0.10,
            "member_mean_format_coverage": 0.98,
            "non_member_mean_format_coverage": 0.28,
            "member_exact_reconstruction_rate": 0.68,
            "non_member_exact_reconstruction_rate": 0.03,
            "generation_failure_rate": 0.12,
            "runtime_seconds": 11.0,
            "failure_reason": "",
            "config_repr": "Config(...)",
        },
        {
            "study_name": "ablation_domain_stack_control",
            "run_name": "domain-fiqa-faiss-bge",
            "started_at": "2026-03-28 12:22:00",
            "finished_at": "2026-03-28 12:30:00",
            "status": "success",
            "dataset": "fiqa",
            "dataset_loader": "fiqa",
            "model_provider": "openai",
            "llm_model": "gpt-4o-mini",
            "llm_model_name": "gpt-4o-mini",
            "model_family": "gpt-4o",
            "model_size_label": "mini",
            "model_params_b": None,
            "closed_weights": True,
            "embedding_model": "bge-small-en-v1.5",
            "embedding_model_name": "BAAI/bge-small-en-v1.5",
            "retriever_type": "faiss",
            "num_masks": 10,
            "retriever_k": 5,
            "gamma": 0.5,
            "index_size": 500,
            "eval_size": 50,
            "member_samples": 50,
            "non_member_samples": 50,
            "auc": 0.98,
            "accuracy": 0.91,
            "precision": 0.92,
            "recall": 0.90,
            "f1": 0.91,
            "retrieval_recall": 1.0,
            "member_mean_mask_accuracy": 0.89,
            "non_member_mean_mask_accuracy": 0.15,
            "member_mean_format_coverage": 0.96,
            "non_member_mean_format_coverage": 0.33,
            "member_exact_reconstruction_rate": 0.59,
            "non_member_exact_reconstruction_rate": 0.04,
            "generation_failure_rate": 0.18,
            "runtime_seconds": 8.0,
            "failure_reason": "",
            "config_repr": "Config(...)",
        },
        {
            "study_name": "ablation_domain_stack_control",
            "run_name": "domain-fiqa-bm25-mini",
            "started_at": "2026-03-28 12:31:00",
            "finished_at": "2026-03-28 12:39:00",
            "status": "success",
            "dataset": "fiqa",
            "dataset_loader": "fiqa",
            "model_provider": "openai",
            "llm_model": "gpt-4o-mini",
            "llm_model_name": "gpt-4o-mini",
            "model_family": "gpt-4o",
            "model_size_label": "mini",
            "model_params_b": None,
            "closed_weights": True,
            "embedding_model": "all-minilm-l6-v2",
            "embedding_model_name": "sentence-transformers/all-MiniLM-L6-v2",
            "retriever_type": "bm25",
            "num_masks": 10,
            "retriever_k": 5,
            "gamma": 0.5,
            "index_size": 500,
            "eval_size": 50,
            "member_samples": 50,
            "non_member_samples": 50,
            "auc": 0.975,
            "accuracy": 0.90,
            "precision": 0.91,
            "recall": 0.89,
            "f1": 0.90,
            "retrieval_recall": 1.0,
            "member_mean_mask_accuracy": 0.87,
            "non_member_mean_mask_accuracy": 0.16,
            "member_mean_format_coverage": 0.94,
            "non_member_mean_format_coverage": 0.35,
            "member_exact_reconstruction_rate": 0.55,
            "non_member_exact_reconstruction_rate": 0.05,
            "generation_failure_rate": 0.22,
            "runtime_seconds": 8.5,
            "failure_reason": "",
            "config_repr": "Config(...)",
        },
    ]
    report_path = tmp_path / "special-report.md"
    write_structured_records(records, tmp_path / "runs.jsonl")
    dataframe = load_structured_records(tmp_path / "runs.jsonl")
    generate_report(dataframe, report_path)
    report_text = report_path.read_text(encoding="utf-8")
    assert "Model Scale Comparison" in report_text
    assert "Domain vs Retrieval Stack Control" in report_text


def test_legacy_parser_reads_existing_format(tmp_path):
    markdown = """## Run 2026-02-23 20:10:28.507740
- **Config**: Config(LLM=llama3, Data=healthcaremagic, Emb=sentence-transformers/all-MiniLM-L6-v2, Ret=faiss, M=5, K=3, Idx=500, Eval=50)
- **Num Masks**: 5
- **Retriever K**: 3
- **AUC**: 0.9520
- **Retrieval Recall**: 1.0000
- **Index Size**: 400
- **Eval Samples**: 100 (M:50, NM:50)
---
"""
    input_path = tmp_path / "experiment_results.md"
    input_path.write_text(markdown, encoding="utf-8")
    dataframe = parse_legacy_markdown(input_path)
    assert len(dataframe) == 1
    assert dataframe.iloc[0]["Dataset"] == "healthcaremagic"
    assert float(dataframe.iloc[0]["AUC"]) == 0.9520
