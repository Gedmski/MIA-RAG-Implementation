from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Iterable

from .config import ExperimentSpec, MIAConfig, dump_yaml, expand_experiment_configs, load_experiment_spec
from .datasets import get_dataset_loader, prepare_dataset_split
from .pipeline import run_single_experiment
from .reporting import build_summary_dataframe, generate_plots, generate_report, write_summary_csv, write_structured_records, write_legacy_snapshots


def _timestamp() -> datetime:
    return datetime.now()


def _run_name(config: MIAConfig) -> str:
    return (
        f"{config.dataset_name}-{config.llm_model}-{config.retriever_type}-"
        f"m{config.num_masks}-k{config.retriever_k}"
    )


def create_run_directory(results_root: str | Path) -> Path:
    timestamp = _timestamp()
    run_dir = Path(results_root) / timestamp.strftime("%Y-%m-%d") / timestamp.strftime("%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def _serialize_spec(spec: ExperimentSpec, configs: list[MIAConfig]) -> dict:
    payload = spec.to_dict()
    payload["resolved_run_count"] = len(configs)
    payload["resolved_configs"] = [config.to_dict() for config in configs]
    return payload


def _write_failures(failures: Iterable[dict], path: str | Path) -> None:
    with Path(path).open("w", encoding="utf-8") as handle:
        for record in failures:
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")


def _build_failure_record(config: MIAConfig, started_at: datetime, finished_at: datetime, error: Exception) -> dict:
    return {
        "run_name": _run_name(config),
        "started_at": started_at.isoformat(sep=" ", timespec="seconds"),
        "finished_at": finished_at.isoformat(sep=" ", timespec="seconds"),
        "status": "failed",
        "dataset": config.dataset_name,
        "dataset_loader": config.dataset_loader,
        "llm_model": config.llm_model,
        "embedding_model": config.embedding_model,
        "retriever_type": config.retriever_type,
        "num_masks": config.num_masks,
        "retriever_k": config.retriever_k,
        "index_size": config.index_size,
        "eval_size": config.eval_size,
        "member_samples": 0,
        "non_member_samples": 0,
        "auc": None,
        "retrieval_recall": None,
        "runtime_seconds": round((finished_at - started_at).total_seconds(), 4),
        "failure_reason": str(error),
        "config_repr": config.compat_repr(),
    }


def run_experiments(config_path: str | Path) -> Path:
    spec = load_experiment_spec(config_path)
    configs = expand_experiment_configs(spec)
    run_dir = create_run_directory(spec.paths.results_root)
    dump_yaml(_serialize_spec(spec, configs), run_dir / "resolved_config.yaml")

    dataset_cache: dict[str, object] = {}
    records: list[dict] = []
    failures: list[dict] = []

    for config in configs:
        started_at = _timestamp()
        try:
            if config.dataset_name not in dataset_cache:
                loader = get_dataset_loader(config.dataset_loader)
                dataset_spec = next(item for item in spec.datasets if item.name == config.dataset_name)
                documents = loader.load_documents(dataset_spec)
                dataset_cache[config.dataset_name] = prepare_dataset_split(
                    documents,
                    index_size=config.index_size,
                    eval_size=config.eval_size,
                    seed=config.seed,
                )
            split = dataset_cache[config.dataset_name]
            result = run_single_experiment(config, split)
            finished_at = _timestamp()
            record = {
                "run_name": _run_name(config),
                "started_at": started_at.isoformat(sep=" ", timespec="seconds"),
                "finished_at": finished_at.isoformat(sep=" ", timespec="seconds"),
                **result,
            }
            records.append(record)
        except Exception as error:
            finished_at = _timestamp()
            failure_record = _build_failure_record(config, started_at, finished_at, error)
            failures.append(failure_record)
            records.append(failure_record)
            if not spec.runtime.continue_on_error:
                break

    summary = build_summary_dataframe(records)
    write_structured_records(records, run_dir / "runs.jsonl")
    _write_failures(failures, run_dir / "failures.jsonl")
    write_summary_csv(summary, run_dir / "summary.csv")
    generate_report(summary, run_dir / "report.md")
    if spec.reporting.generate_plots:
        generate_plots(summary, run_dir / "plots")
    if spec.reporting.copy_legacy_outputs:
        write_legacy_snapshots(
            summary,
            spec.paths.legacy_experiment_log,
            spec.paths.legacy_csv,
            spec.paths.legacy_report,
        )
    return run_dir
