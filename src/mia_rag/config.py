from __future__ import annotations

from dataclasses import asdict, dataclass, field
from itertools import product
from pathlib import Path
from typing import Any

import yaml


COMMON_REQUIRED_TOP_LEVEL_KEYS = {
    "paths",
    "datasets",
    "models",
    "retrievers",
    "embeddings",
    "runtime",
    "reporting",
}
LEGACY_REQUIRED_KEY = "sweeps"
STUDY_REQUIRED_KEY = "studies"
LEGACY_STUDY_NAME = "default_sweep"
SUPPORTED_STUDY_FIELDS = {
    "dataset",
    "model",
    "retriever",
    "embedding",
    "num_masks",
    "retriever_k",
    "gamma",
    "index_size",
    "eval_size",
    "seed",
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
class ModelSpec:
    alias: str
    provider: str = "ollama"
    model_name: str | None = None
    api_mode: str | None = None
    family: str | None = None
    size_label: str | None = None
    params_b: float | None = None
    closed_weights: bool | None = None
    enabled: bool = True
    options: dict[str, Any] = field(default_factory=dict)

    def resolved_model_name(self) -> str:
        return self.model_name or self.alias


@dataclass
class EmbeddingSpec:
    alias: str
    model_name: str | None = None
    provider: str | None = None
    enabled: bool = True
    options: dict[str, Any] = field(default_factory=dict)

    def resolved_model_name(self) -> str:
        return self.model_name or self.alias


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
    gamma: float = 0.5
    continue_on_error: bool = True
    limit_runs: int | None = None
    llm_temperature: float = 0.0


@dataclass
class ReportingConfig:
    generate_plots: bool = True
    copy_legacy_outputs: bool = True


@dataclass
class StudySpec:
    name: str
    description: str = ""
    overrides: dict[str, Any] = field(default_factory=dict)
    sweep: dict[str, list[Any]] = field(default_factory=dict)


@dataclass
class ExperimentSpec:
    paths: PathsConfig
    datasets: list[DatasetSpec]
    models: dict[str, ModelSpec]
    retrievers: list[str]
    embeddings: dict[str, EmbeddingSpec]
    sweeps: SweepSpec | None
    runtime: RuntimeConfig
    reporting: ReportingConfig
    defaults: dict[str, Any] = field(default_factory=dict)
    studies: list[StudySpec] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def dataset_map(self) -> dict[str, DatasetSpec]:
        return {dataset.name: dataset for dataset in self.datasets}

    def enabled_datasets(self) -> list[DatasetSpec]:
        return [dataset for dataset in self.datasets if dataset.enabled]

    def enabled_models(self) -> list[ModelSpec]:
        return [model for model in self.models.values() if model.enabled]

    def enabled_embeddings(self) -> list[EmbeddingSpec]:
        return [embedding for embedding in self.embeddings.values() if embedding.enabled]


@dataclass
class MIAConfig:
    study_name: str
    model_provider: str
    llm_model: str
    llm_model_name: str
    model_family: str | None
    model_size_label: str | None
    model_params_b: float | None
    closed_weights: bool | None
    embedding_model: str
    embedding_model_name: str
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
    gamma: float
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


@dataclass
class ResolvedStudy:
    name: str
    description: str = ""
    configs: list[MIAConfig] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "resolved_run_count": len(self.configs),
            "resolved_configs": [config.to_dict() for config in self.configs],
        }


def _split_known_fields(raw: dict[str, Any], known_keys: set[str]) -> tuple[dict[str, Any], dict[str, Any]]:
    known: dict[str, Any] = {}
    extra: dict[str, Any] = {}
    for key, value in raw.items():
        if key in known_keys:
            known[key] = value
        else:
            extra[key] = value
    return known, extra


def _validate_top_level_keys(path: Path, data: dict[str, Any]) -> None:
    missing = COMMON_REQUIRED_TOP_LEVEL_KEYS.difference(data)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Config file {path} is missing required sections: {missing_list}")
    if LEGACY_REQUIRED_KEY not in data and STUDY_REQUIRED_KEY not in data:
        raise ValueError(f"Config file {path} must define either '{LEGACY_REQUIRED_KEY}' or '{STUDY_REQUIRED_KEY}'.")


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    _validate_top_level_keys(path, data)
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


def _parse_datasets(raw: Any) -> list[DatasetSpec]:
    if isinstance(raw, list):
        return [_parse_dataset_spec(item) for item in raw]
    if isinstance(raw, dict):
        parsed: list[DatasetSpec] = []
        for name, value in raw.items():
            if not isinstance(value, dict):
                raise ValueError(f"Dataset '{name}' must map to an object of options.")
            parsed.append(_parse_dataset_spec({"name": name, **value}))
        return parsed
    raise ValueError("Datasets section must be a list or mapping.")


def _parse_models(raw: Any) -> dict[str, ModelSpec]:
    if isinstance(raw, list):
        return {
            alias: ModelSpec(alias=alias, provider="ollama", model_name=alias)
            for alias in raw
        }
    if not isinstance(raw, dict):
        raise ValueError("Models section must be a list or mapping.")

    parsed: dict[str, ModelSpec] = {}
    for alias, value in raw.items():
        if not isinstance(value, dict):
            raise ValueError(f"Model '{alias}' must map to an object with provider metadata.")
        if "provider" not in value:
            raise ValueError(f"Model '{alias}' is missing required 'provider' metadata.")
        options = dict(value)
        provider = str(options.pop("provider"))
        model_name = str(options.pop("model_name", alias))
        api_mode = options.pop("api_mode", None)
        family = options.pop("family", None)
        size_label = options.pop("size_label", None)
        params_b = options.pop("params_b", None)
        if params_b is not None:
            params_b = float(params_b)
        closed_weights = options.pop("closed_weights", None)
        if closed_weights is not None:
            closed_weights = bool(closed_weights)
        enabled = bool(options.pop("enabled", True))
        parsed[alias] = ModelSpec(
            alias=alias,
            provider=provider,
            model_name=model_name,
            api_mode=api_mode,
            family=family,
            size_label=size_label,
            params_b=params_b,
            closed_weights=closed_weights,
            enabled=enabled,
            options=options,
        )
    return parsed


def _parse_embeddings(raw: Any) -> dict[str, EmbeddingSpec]:
    if isinstance(raw, list):
        return {
            alias: EmbeddingSpec(alias=alias, model_name=alias)
            for alias in raw
        }
    if not isinstance(raw, dict):
        raise ValueError("Embeddings section must be a list or mapping.")

    parsed: dict[str, EmbeddingSpec] = {}
    for alias, value in raw.items():
        if isinstance(value, str):
            parsed[alias] = EmbeddingSpec(alias=alias, model_name=value)
            continue
        if not isinstance(value, dict):
            raise ValueError(f"Embedding '{alias}' must map to an object or model string.")
        options = dict(value)
        model_name = str(options.pop("model_name", alias))
        provider = options.pop("provider", None)
        enabled = bool(options.pop("enabled", True))
        parsed[alias] = EmbeddingSpec(
            alias=alias,
            model_name=model_name,
            provider=provider,
            enabled=enabled,
            options=options,
        )
    return parsed


def _parse_retrievers(raw: Any) -> list[str]:
    if isinstance(raw, list):
        return list(raw)
    if not isinstance(raw, dict):
        raise ValueError("Retrievers section must be a list or mapping.")

    parsed: list[str] = []
    for alias, value in raw.items():
        if isinstance(value, dict) and not value.get("enabled", True):
            continue
        parsed.append(alias)
    return parsed


def _validate_study_fields(source_name: str, raw: dict[str, Any]) -> dict[str, Any]:
    unknown = set(raw).difference(SUPPORTED_STUDY_FIELDS)
    if unknown:
        unknown_list = ", ".join(sorted(unknown))
        raise ValueError(f"{source_name} uses unsupported fields: {unknown_list}")
    return raw


def _parse_studies(raw: Any) -> list[StudySpec]:
    if raw is None:
        return []
    if not isinstance(raw, dict):
        raise ValueError("Studies section must be a mapping of study names to objects.")

    studies: list[StudySpec] = []
    for name, value in raw.items():
        if not isinstance(value, dict):
            raise ValueError(f"Study '{name}' must map to an object.")
        description = str(value.get("description", ""))
        overrides = _validate_study_fields(f"Study '{name}' overrides", dict(value.get("overrides", {})))
        sweep = dict(value.get("sweep", {}))
        _validate_study_fields(f"Study '{name}' sweep", sweep)
        for field_name, field_values in sweep.items():
            if not isinstance(field_values, list) or not field_values:
                raise ValueError(f"Study '{name}' sweep field '{field_name}' must be a non-empty list.")
        studies.append(
            StudySpec(
                name=name,
                description=description,
                overrides=overrides,
                sweep=sweep,
            )
        )
    return studies


def _parse_defaults(raw: Any) -> dict[str, Any]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError("Defaults section must be a mapping.")
    return _validate_study_fields("Defaults", dict(raw))


def load_experiment_spec(path: str | Path) -> ExperimentSpec:
    config_path = Path(path)
    data = _load_yaml(config_path)
    return ExperimentSpec(
        paths=PathsConfig(**data["paths"]),
        datasets=_parse_datasets(data["datasets"]),
        models=_parse_models(data["models"]),
        retrievers=_parse_retrievers(data["retrievers"]),
        embeddings=_parse_embeddings(data["embeddings"]),
        sweeps=SweepSpec(**data["sweeps"]) if data.get("sweeps") else None,
        runtime=RuntimeConfig(**data["runtime"]),
        reporting=ReportingConfig(**data["reporting"]),
        defaults=_parse_defaults(data.get("defaults")),
        studies=_parse_studies(data.get("studies")),
    )


def _enabled_retrievers(spec: ExperimentSpec) -> list[str]:
    return list(spec.retrievers)


def _require_choice(section: str, value: Any, valid_values: set[str]) -> str:
    if value is None:
        valid_list = ", ".join(sorted(valid_values))
        raise ValueError(f"Study configs must define '{section}'. Available values: {valid_list}")
    choice = str(value)
    if choice not in valid_values:
        valid_list = ", ".join(sorted(valid_values))
        raise ValueError(f"Unknown {section} '{choice}'. Available values: {valid_list}")
    return choice


def _coerce_int(value: Any, field_name: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Field '{field_name}' must be an integer, got {value!r}") from exc


def _coerce_float(value: Any, field_name: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Field '{field_name}' must be numeric, got {value!r}") from exc


def _resolve_study_config(spec: ExperimentSpec, study: StudySpec, values: dict[str, Any]) -> MIAConfig:
    datasets = spec.dataset_map()
    dataset_name = _require_choice("dataset", values.get("dataset"), set(datasets))
    dataset = datasets[dataset_name]
    if not dataset.enabled:
        raise ValueError(f"Dataset '{dataset_name}' is disabled and cannot be referenced by study '{study.name}'.")

    model_alias = _require_choice("model", values.get("model"), set(spec.models))
    model = spec.models[model_alias]
    if not model.enabled:
        raise ValueError(f"Model '{model_alias}' is disabled and cannot be referenced by study '{study.name}'.")

    retriever_name = _require_choice("retriever", values.get("retriever"), set(_enabled_retrievers(spec)))

    embedding_alias = _require_choice("embedding", values.get("embedding"), set(spec.embeddings))
    embedding = spec.embeddings[embedding_alias]
    if not embedding.enabled:
        raise ValueError(
            f"Embedding '{embedding_alias}' is disabled and cannot be referenced by study '{study.name}'."
        )

    dataset_seed = dataset.seed if dataset.seed is not None else spec.runtime.seed
    return MIAConfig(
        study_name=study.name,
        model_provider=model.provider,
        llm_model=model.alias,
        llm_model_name=model.resolved_model_name(),
        model_family=model.family,
        model_size_label=model.size_label,
        model_params_b=model.params_b,
        closed_weights=model.closed_weights,
        embedding_model=embedding.alias,
        embedding_model_name=embedding.resolved_model_name(),
        dataset_name=dataset.name,
        dataset_loader=dataset.loader,
        dataset_id=dataset.dataset_id,
        dataset_config=dataset.dataset_config,
        dataset_split=dataset.split,
        dataset_streaming=dataset.streaming,
        dataset_category=dataset.category,
        dataset_loader_options=dict(dataset.loader_options),
        proxy_model=spec.runtime.proxy_model,
        num_masks=_coerce_int(values.get("num_masks"), "num_masks"),
        retriever_k=_coerce_int(values.get("retriever_k"), "retriever_k"),
        gamma=_coerce_float(values.get("gamma", spec.runtime.gamma), "gamma"),
        masking_strategy=spec.runtime.masking_strategy,
        use_spelling_correction=spec.runtime.use_spelling_correction,
        retriever_type=retriever_name,
        index_size=_coerce_int(values.get("index_size", dataset.index_size), "index_size"),
        eval_size=_coerce_int(values.get("eval_size", dataset.eval_size), "eval_size"),
        min_chars=dataset.min_chars,
        max_chars=dataset.max_chars,
        seed=_coerce_int(values.get("seed", dataset_seed), "seed"),
        llm_temperature=spec.runtime.llm_temperature,
    )


def _expand_legacy_configs(spec: ExperimentSpec) -> list[MIAConfig]:
    configs: list[MIAConfig] = []
    if spec.sweeps is None:
        return configs
    for dataset in spec.enabled_datasets():
        dataset_seed = dataset.seed if dataset.seed is not None else spec.runtime.seed
        for model in spec.enabled_models():
            for embedding in spec.enabled_embeddings():
                for retriever in _enabled_retrievers(spec):
                    for num_masks in spec.sweeps.num_masks:
                        for retriever_k in spec.sweeps.retriever_k:
                            configs.append(
                                MIAConfig(
                                    study_name=LEGACY_STUDY_NAME,
                                    model_provider=model.provider,
                                    llm_model=model.alias,
                                    llm_model_name=model.resolved_model_name(),
                                    model_family=model.family,
                                    model_size_label=model.size_label,
                                    model_params_b=model.params_b,
                                    closed_weights=model.closed_weights,
                                    embedding_model=embedding.alias,
                                    embedding_model_name=embedding.resolved_model_name(),
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
                                    gamma=spec.runtime.gamma,
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
    return configs


def _expand_study_configs(spec: ExperimentSpec) -> list[ResolvedStudy]:
    if not spec.studies:
        return [ResolvedStudy(name=LEGACY_STUDY_NAME, description="Legacy full sweep", configs=_expand_legacy_configs(spec))]

    studies: list[ResolvedStudy] = []
    for study in spec.studies:
        base_values = dict(spec.defaults)
        base_values.update(study.overrides)
        sweep_fields = list(study.sweep.keys())
        sweep_lists = [study.sweep[field_name] for field_name in sweep_fields]
        combinations = product(*sweep_lists) if sweep_fields else [()]

        configs: list[MIAConfig] = []
        for combo in combinations:
            resolved_values = dict(base_values)
            resolved_values.update(dict(zip(sweep_fields, combo)))
            configs.append(_resolve_study_config(spec, study, resolved_values))
        studies.append(ResolvedStudy(name=study.name, description=study.description, configs=configs))
    return studies


def _apply_limit_runs(studies: list[ResolvedStudy], limit_runs: int | None) -> list[ResolvedStudy]:
    if limit_runs is None:
        return studies

    remaining = limit_runs
    limited: list[ResolvedStudy] = []
    for study in studies:
        if remaining <= 0:
            break
        sliced = study.configs[:remaining]
        remaining -= len(sliced)
        if sliced:
            limited.append(ResolvedStudy(name=study.name, description=study.description, configs=sliced))
    return limited


def expand_experiment_studies(spec: ExperimentSpec) -> list[ResolvedStudy]:
    studies = _expand_study_configs(spec)
    return _apply_limit_runs(studies, spec.runtime.limit_runs)


def expand_experiment_configs(spec: ExperimentSpec) -> list[MIAConfig]:
    return [config for study in expand_experiment_studies(spec) for config in study.configs]


def dump_yaml(data: dict[str, Any], path: str | Path) -> None:
    with Path(path).open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False)
