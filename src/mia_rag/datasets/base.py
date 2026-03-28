from __future__ import annotations

import abc
import re
from typing import Any, Iterable

from ..config import DatasetSpec
from ..types import DocumentRecord


def normalize_text(text: str, min_chars: int, max_chars: int) -> str | None:
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    if len(cleaned) < min_chars:
        return None
    return cleaned[:max_chars]


def _load_huggingface_split(spec: DatasetSpec):
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise ImportError("datasets is required to load Hugging Face sources") from exc

    if not spec.dataset_id:
        raise ValueError(f"Dataset {spec.name} is missing dataset_id")

    kwargs = {
        "split": spec.split,
        "streaming": spec.streaming,
    }
    if spec.dataset_config:
        return load_dataset(spec.dataset_id, spec.dataset_config, **kwargs)
    return load_dataset(spec.dataset_id, **kwargs)


class DatasetLoader(abc.ABC):
    loader_name = "base"

    @abc.abstractmethod
    def iter_records(self, spec: DatasetSpec) -> Iterable[DocumentRecord]:
        raise NotImplementedError

    def inspect_source(self, spec: DatasetSpec) -> dict[str, Any]:
        try:
            dataset = self.load_split(spec)
            iterator = iter(dataset)
            first_row = next(iterator)
            return {
                "first_row_keys": sorted(first_row.keys()) if isinstance(first_row, dict) else [],
            }
        except Exception as exc:
            return {
                "inspection_error": str(exc),
            }

    def load_documents(self, spec: DatasetSpec) -> list[DocumentRecord]:
        documents: list[DocumentRecord] = []
        seen_texts: set[str] = set()
        required = spec.required_documents()

        for index, record in enumerate(self.iter_records(spec)):
            normalized = normalize_text(record.text, spec.min_chars, spec.max_chars)
            if not normalized or normalized in seen_texts:
                continue
            seen_texts.add(normalized)
            metadata = dict(record.metadata)
            metadata.setdefault("dataset", spec.name)
            metadata.setdefault("loader", self.loader_name)
            metadata.setdefault("row_index", index)
            documents.append(DocumentRecord(doc_id=str(record.doc_id), text=normalized, metadata=metadata))
            if len(documents) >= required:
                break

        if len(documents) < required:
            inspection = self.inspect_source(spec)
            raise ValueError(
                f"Dataset {spec.name} produced {len(documents)} documents, fewer than required {required}. "
                f"Loader options={spec.loader_options}. Inspection={inspection}"
            )
        return documents

    @staticmethod
    def load_split(spec: DatasetSpec):
        return _load_huggingface_split(spec)
