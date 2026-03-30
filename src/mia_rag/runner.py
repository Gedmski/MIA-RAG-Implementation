from __future__ import annotations

from dataclasses import replace
from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any, Iterable

from .config import (
    DatasetSpec,
    ExperimentSpec,
    MIAConfig,
    ResolvedStudy,
    dump_yaml,
    expand_experiment_studies,
    load_experiment_spec,
)
from .datasets import get_dataset_loader, prepare_dataset_split
from .pipeline import run_single_experiment
from .reporting import (
    build_summary_dataframe,
    generate_plots,
    generate_report,
    write_summary_csv,
    write_structured_records,
    write_legacy_snapshots,
)


def _timestamp() -> datetime:
    return datetime.now()


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    return cleaned.strip("-") or "study"


def _run_name(config: MIAConfig) -> str:
    return (
        f"{_slugify(config.study_name)}-{_slugify(config.dataset_name)}-{_slugify(config.llm_model)}-"
        f"{_slugify(config.retriever_type)}-{_slugify(config.embedding_model)}-"
        f"m{config.num_masks}-k{config.retriever_k}-g{config.gamma:.2f}-"
        f"idx{config.index_size}-eval{config.eval_size}-seed{config.seed}"
    )


def create_run_directory(results_root: str | Path) -> Path:
    timestamp = _timestamp()
    run_dir = Path(results_root) / timestamp.strftime("%Y-%m-%d") / timestamp.strftime("%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def _study_directory(root: Path, study_name: str) -> Path:
    path = root / "studies" / _slugify(study_name)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _serialize_spec(spec: ExperimentSpec, studies: list[ResolvedStudy]) -> dict[str, Any]:
    payload = spec.to_dict()
    payload["resolved_study_count"] = len(studies)
    payload["resolved_run_count"] = sum(len(study.configs) for study in studies)
    payload["resolved_studies"] = [study.to_dict() for study in studies]
    payload["resolved_configs"] = [config.to_dict() for study in studies for config in study.configs]
    return payload


def _serialize_study(spec: ExperimentSpec, study: ResolvedStudy) -> dict[str, Any]:
    payload = spec.to_dict()
    payload["resolved_study_count"] = 1
    payload["resolved_run_count"] = len(study.configs)
    payload["resolved_studies"] = [study.to_dict()]
    payload["resolved_configs"] = [config.to_dict() for config in study.configs]
    return payload


def _write_failures(failures: Iterable[dict[str, Any]], path: str | Path) -> None:
    with Path(path).open("w", encoding="utf-8") as handle:
        for record in failures:
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")


def _build_failure_record(config: MIAConfig, started_at: datetime, finished_at: datetime, error: Exception) -> dict[str, Any]:
    return {
        "study_name": config.study_name,
        "run_name": _run_name(config),
        "started_at": started_at.isoformat(sep=" ", timespec="seconds"),
        "finished_at": finished_at.isoformat(sep=" ", timespec="seconds"),
        "status": "failed",
        "dataset": config.dataset_name,
        "dataset_loader": config.dataset_loader,
        "model_provider": config.model_provider,
        "llm_model": config.llm_model,
        "llm_model_name": config.llm_model_name,
        "embedding_model": config.embedding_model,
        "embedding_model_name": config.embedding_model_name,
        "retriever_type": config.retriever_type,
        "num_masks": config.num_masks,
        "retriever_k": config.retriever_k,
        "gamma": config.gamma,
        "index_size": config.index_size,
        "eval_size": config.eval_size,
        "member_samples": 0,
        "non_member_samples": 0,
        "auc": None,
        "accuracy": None,
        "precision": None,
        "recall": None,
        "f1": None,
        "retrieval_recall": None,
        "runtime_seconds": round((finished_at - started_at).total_seconds(), 4),
        "failure_reason": str(error),
        "config_repr": config.compat_repr(),
    }


def _freeze_value(value: Any) -> Any:
    if isinstance(value, dict):
        return tuple(sorted((key, _freeze_value(item)) for key, item in value.items()))
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_value(item) for item in value)
    return value


def _dataset_cache_key(config: MIAConfig) -> tuple[Any, ...]:
    return (
        config.dataset_name,
        config.dataset_loader,
        config.dataset_id,
        config.dataset_config,
        config.dataset_split,
        config.dataset_streaming,
        config.dataset_category,
        config.min_chars,
        config.max_chars,
        _freeze_value(config.dataset_loader_options),
        config.index_size,
        config.eval_size,
        config.seed,
    )


def _dataset_spec_for_config(spec: ExperimentSpec, config: MIAConfig) -> DatasetSpec:
    dataset_spec = next(item for item in spec.datasets if item.name == config.dataset_name)
    return replace(dataset_spec, index_size=config.index_size, eval_size=config.eval_size, seed=config.seed)


def _write_outputs(
    records: list[dict[str, Any]],
    failures: list[dict[str, Any]],
    output_dir: Path,
    *,
    generate_plot_assets: bool,
) -> None:
    summary = build_summary_dataframe(records)
    write_structured_records(records, output_dir / "runs.jsonl")
    _write_failures(failures, output_dir / "failures.jsonl")
    write_summary_csv(summary, output_dir / "summary.csv")
    generate_report(summary, output_dir / "report.md")
    if generate_plot_assets:
        generate_plots(summary, output_dir / "plots")


def _run_study(
    spec: ExperimentSpec,
    study: ResolvedStudy,
    *,
    dataset_cache: dict[tuple[Any, ...], object],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for index, config in enumerate(study.configs, start=1):
        started_at = _timestamp()
        try:
            print(
                f"[{study.name} {index}/{len(study.configs)}] dataset={config.dataset_name} model={config.llm_model} "
                f"retriever={config.retriever_type} embedding={config.embedding_model} "
                f"M={config.num_masks} K={config.retriever_k} gamma={config.gamma}"
            )
            cache_key = _dataset_cache_key(config)
            if cache_key not in dataset_cache:
                print(f"  loading dataset '{config.dataset_name}' with loader '{config.dataset_loader}'")
                loader = get_dataset_loader(config.dataset_loader)
                dataset_spec = _dataset_spec_for_config(spec, config)
                documents = loader.load_documents(dataset_spec)
                print(f"  normalized documents available: {len(documents)}")
                dataset_cache[cache_key] = prepare_dataset_split(
                    documents,
                    index_size=config.index_size,
                    eval_size=config.eval_size,
                    seed=config.seed,
                )
            split = dataset_cache[cache_key]
            result = run_single_experiment(config, split)
            finished_at = _timestamp()
            record = {
                "run_name": _run_name(config),
                "started_at": started_at.isoformat(sep=" ", timespec="seconds"),
                "finished_at": finished_at.isoformat(sep=" ", timespec="seconds"),
                **result,
            }
            records.append(record)
            print(
                f"  success auc={record['auc']:.4f} f1={record['f1']:.4f} "
                f"recall={record['retrieval_recall']:.4f} runtime={record['runtime_seconds']:.1f}s"
            )
        except Exception as error:
            finished_at = _timestamp()
            failure_record = _build_failure_record(config, started_at, finished_at, error)
            failures.append(failure_record)
            records.append(failure_record)
            print(f"  failed: {error}")
            if not spec.runtime.continue_on_error:
                break
    return records, failures


def run_experiments(config_path: str | Path) -> Path:
    spec = load_experiment_spec(config_path)
    studies = expand_experiment_studies(spec)
    total_runs = sum(len(study.configs) for study in studies)
    run_dir = create_run_directory(spec.paths.results_root)

    print(f"Loaded config: {config_path}")
    print(f"Resolved {len(studies)} studies / {total_runs} runs")
    print(f"Writing outputs to: {run_dir}")
    dump_yaml(_serialize_spec(spec, studies), run_dir / "resolved_config.yaml")

    dataset_cache: dict[tuple[Any, ...], object] = {}
    combined_records: list[dict[str, Any]] = []
    combined_failures: list[dict[str, Any]] = []

    for study in studies:
        print(f"Starting study '{study.name}' with {len(study.configs)} runs")
        study_dir = _study_directory(run_dir, study.name)
        dump_yaml(_serialize_study(spec, study), study_dir / "resolved_config.yaml")
        study_records, study_failures = _run_study(spec, study, dataset_cache=dataset_cache)
        _write_outputs(
            study_records,
            study_failures,
            study_dir,
            generate_plot_assets=spec.reporting.generate_plots,
        )
        combined_records.extend(study_records)
        combined_failures.extend(study_failures)

    _write_outputs(
        combined_records,
        combined_failures,
        run_dir,
        generate_plot_assets=spec.reporting.generate_plots,
    )
    if spec.reporting.copy_legacy_outputs:
        combined_summary = build_summary_dataframe(combined_records)
        write_legacy_snapshots(
            combined_summary,
            spec.paths.legacy_experiment_log,
            spec.paths.legacy_csv,
            spec.paths.legacy_report,
        )
    return run_dir
