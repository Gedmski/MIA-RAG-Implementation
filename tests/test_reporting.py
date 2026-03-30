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

    report_path = tmp_path / "report.md"
    generate_report(dataframe, report_path)
    report_text = report_path.read_text(encoding="utf-8")
    assert "Study Overview" in report_text
    assert "Dataset: healthcaremagic" in report_text
    assert "Best F1" in report_text


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
