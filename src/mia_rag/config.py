from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml


REQUIRED_TOP_LEVEL_KEYS = {
    "paths",
    "datasets",
    "models",
    "retrievers",
    "embeddings",
    "sweeps",
    "runtime",
    "reporting",
}


@dataclass
class PathsConfig:
    results_root: str = "results"
    legacy_experiment_log: str = "experiment_results.md"
    legacy_csv: str = "experiment_data.csv"
    legacy_report: str = "results_report.md"


@dataclass
class DatasetSpec:
    name: str
    loader: str
    enabled: bool = True
    dataset_id: str | None = None
    dataset_config: str | None = None
    split: str | None = None
    streaming: bool = False
    index_size: int = 500
    eval_size: int = 50
    min_chars: int = 200
    max_chars: int = 2500
    category: str | None = None
    seed: int | None = None
    loader_options: dict[str, Any] = field(default_factory=dict)

    def required_documents(self) -> int:
        return self.index_size + self.eval_size


@dataclass
class SweepSpec:
    num_masks: list[int] = field(default_factory=lambda: [1, 3, 5, 7, 10, 15, 20])
    retriever_k: list[int] = field(default_factory=lambda: [1, 3, 5, 10, 15])


@dataclass
class RuntimeConfig:
    proxy_model: str = "gpt2"
    masking_strategy: str = "hard"
    use_spelling_correction: bool = True
    seed: int = 42
    continue_on_error: bool = True
    limit_runs: int | None = None
    llm_temperature: float = 0.0


@dataclass
class ReportingConfig:
    generate_plots: bool = True
    copy_legacy_outputs: bool = True


@dataclass
class ExperimentSpec:
    paths: PathsConfig
    datasets: list[DatasetSpec]
    models: list[str]
    retrievers: list[str]
    embeddings: list[str]
    sweeps: SweepSpec
    runtime: RuntimeConfig
    reporting: ReportingConfig

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MIAConfig:
    llm_model: str
    embedding_model: str
    dataset_name: str
    dataset_loader: str
    dataset_id: str | None
    dataset_config: str | None
    dataset_split: str | None
    dataset_streaming: bool
    dataset_category: str | None
    dataset_loader_options: dict[str, Any]
    proxy_model: str
    num_masks: int
    retriever_k: int
    masking_strategy: str
    use_spelling_correction: bool
    retriever_type: str
    index_size: int
    eval_size: int
    min_chars: int
    max_chars: int
    seed: int
    llm_temperature: float = 0.0

    def compat_repr(self) -> str:
        return (
            f"Config(LLM={self.llm_model}, Data={self.dataset_name}, Emb={self.embedding_model}, "
            f"Ret={self.retriever_type}, M={self.num_masks}, K={self.retriever_k}, "
            f"Idx={self.index_size}, Eval={self.eval_size})"
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _split_known_fields(raw: dict[str, Any], known_keys: set[str]) -> tuple[dict[str, Any], dict[str, Any]]:
    known: dict[str, Any] = {}
    extra: dict[str, Any] = {}
    for key, value in raw.items():
        if key in known_keys:
            known[key] = value
        else:
            extra[key] = value
    return known, extra


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    missing = REQUIRED_TOP_LEVEL_KEYS.difference(data)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Config file {path} is missing required sections: {missing_list}")
    return data


def _parse_dataset_spec(raw: dict[str, Any]) -> DatasetSpec:
    known_keys = {
        "name",
        "loader",
        "enabled",
        "dataset_id",
        "dataset_config",
        "split",
        "streaming",
        "index_size",
        "eval_size",
        "min_chars",
        "max_chars",
        "category",
        "seed",
    }
    known, extra = _split_known_fields(raw, known_keys)
    spec = DatasetSpec(**known)
    spec.loader_options.update(extra)
    return spec


def load_experiment_spec(path: str | Path) -> ExperimentSpec:
    config_path = Path(path)
    data = _load_yaml(config_path)
    return ExperimentSpec(
        paths=PathsConfig(**data["paths"]),
        datasets=[_parse_dataset_spec(item) for item in data["datasets"]],
        models=list(data["models"]),
        retrievers=list(data["retrievers"]),
        embeddings=list(data["embeddings"]),
        sweeps=SweepSpec(**data["sweeps"]),
        runtime=RuntimeConfig(**data["runtime"]),
        reporting=ReportingConfig(**data["reporting"]),
    )


def expand_experiment_configs(spec: ExperimentSpec) -> list[MIAConfig]:
    configs: list[MIAConfig] = []
    for dataset in spec.datasets:
        if not dataset.enabled:
            continue
        dataset_seed = dataset.seed if dataset.seed is not None else spec.runtime.seed
        for model in spec.models:
            for embedding in spec.embeddings:
                for retriever in spec.retrievers:
                    for num_masks in spec.sweeps.num_masks:
                        for retriever_k in spec.sweeps.retriever_k:
                            configs.append(
                                MIAConfig(
                                    llm_model=model,
                                    embedding_model=embedding,
                                    dataset_name=dataset.name,
                                    dataset_loader=dataset.loader,
                                    dataset_id=dataset.dataset_id,
                                    dataset_config=dataset.dataset_config,
                                    dataset_split=dataset.split,
                                    dataset_streaming=dataset.streaming,
                                    dataset_category=dataset.category,
                                    dataset_loader_options=dict(dataset.loader_options),
                                    proxy_model=spec.runtime.proxy_model,
                                    num_masks=num_masks,
                                    retriever_k=retriever_k,
                                    masking_strategy=spec.runtime.masking_strategy,
                                    use_spelling_correction=spec.runtime.use_spelling_correction,
                                    retriever_type=retriever,
                                    index_size=dataset.index_size,
                                    eval_size=dataset.eval_size,
                                    min_chars=dataset.min_chars,
                                    max_chars=dataset.max_chars,
                                    seed=dataset_seed,
                                    llm_temperature=spec.runtime.llm_temperature,
                                )
                            )
    if spec.runtime.limit_runs is not None:
        return configs[: spec.runtime.limit_runs]
    return configs


def dump_yaml(data: dict[str, Any], path: str | Path) -> None:
    with Path(path).open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False)
