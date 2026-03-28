from __future__ import annotations

from typing import Iterable

from ..config import DatasetSpec
from ..types import DocumentRecord
from .base import DatasetLoader


def _first_non_empty(row: dict, keys: list[str]) -> str:
    for key in keys:
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return ""


class HealthCareMagicLoader(DatasetLoader):
    loader_name = "healthcaremagic"

    def iter_records(self, spec: DatasetSpec) -> Iterable[DocumentRecord]:
        dataset = self.load_split(spec)
        text_fields = spec.loader_options.get("text_fields", ["text"])
        question_keys = spec.loader_options.get("question_fields", ["input", "instruction"])
        answer_keys = spec.loader_options.get("answer_fields", ["output", "response"])
        for index, row in enumerate(dataset):
            text = _first_non_empty(row, text_fields)
            if text:
                yield DocumentRecord(
                    doc_id=str(row.get("id", index)),
                    text=text,
                    metadata={"source_id": row.get("id")},
                )
                continue
            question = _first_non_empty(row, question_keys)
            answer = _first_non_empty(row, answer_keys)
            if not question and not answer:
                continue
            text = f"Patient: {question}\nDoctor: {answer}".strip()
            yield DocumentRecord(doc_id=str(row.get("id", index)), text=text, metadata={"source_id": row.get("id")})


class MSMARCOLoader(DatasetLoader):
    loader_name = "msmarco"

    def iter_records(self, spec: DatasetSpec) -> Iterable[DocumentRecord]:
        dataset = self.load_split(spec)
        for row_index, row in enumerate(dataset):
            passages = row.get("passages", {}) or {}
            texts = passages.get("passage_text", []) or []
            for passage_index, passage_text in enumerate(texts):
                if not isinstance(passage_text, str):
                    continue
                record_id = f"{row.get('query_id', row_index)}-{passage_index}"
                yield DocumentRecord(
                    doc_id=record_id,
                    text=passage_text,
                    metadata={"query_id": row.get("query_id"), "passage_index": passage_index},
                )


class NQLoader(DatasetLoader):
    loader_name = "nq"

    def iter_records(self, spec: DatasetSpec) -> Iterable[DocumentRecord]:
        dataset = self.load_split(spec)
        text_keys = spec.loader_options.get(
            "text_fields",
            ["context", "document_text", "passage", "long_answer"],
        )
        for index, row in enumerate(dataset):
            text = _first_non_empty(row, text_keys)
            if not text:
                continue
            yield DocumentRecord(doc_id=str(row.get("id", index)), text=text, metadata={"source_id": row.get("id")})


class FiQALoader(DatasetLoader):
    loader_name = "fiqa"

    def iter_records(self, spec: DatasetSpec) -> Iterable[DocumentRecord]:
        dataset = self.load_split(spec)
        title_field = spec.loader_options.get("title_field", "title")
        text_field = spec.loader_options.get("text_field", "text")
        for index, row in enumerate(dataset):
            title = row.get(title_field, "") or ""
            text = row.get(text_field, "") or ""
            combined = "\n".join(part for part in [title.strip(), text.strip()] if part.strip())
            if not combined:
                continue
            yield DocumentRecord(doc_id=str(row.get("_id", index)), text=combined, metadata={"source_id": row.get("_id")})


class ArxivLoader(DatasetLoader):
    loader_name = "arxiv"

    def iter_records(self, spec: DatasetSpec) -> Iterable[DocumentRecord]:
        dataset = self.load_split(spec)
        title_fields = spec.loader_options.get("title_fields", ["title", "Titles"])
        abstract_fields = spec.loader_options.get("abstract_fields", ["abstract", "Abstracts"])
        category_fields = spec.loader_options.get("category_fields", ["categories", "Categories"])
        fallback_text_fields = spec.loader_options.get("fallback_text_fields", ["text", "summary", "paper"])
        requested_category = (spec.category or "").strip().lower()

        for index, row in enumerate(dataset):
            categories = _first_non_empty(row, category_fields)
            normalized_categories = categories.lower() if categories else ""
            if requested_category and normalized_categories and requested_category not in normalized_categories:
                continue
            title = _first_non_empty(row, title_fields)
            abstract = _first_non_empty(row, abstract_fields)
            if not title and not abstract:
                fallback_text = _first_non_empty(row, fallback_text_fields)
                if not fallback_text:
                    continue
                yield DocumentRecord(
                    doc_id=str(row.get("id", index)),
                    text=fallback_text,
                    metadata={"source_id": row.get("id"), "categories": categories},
                )
                continue
            combined = "\n".join(part for part in [f"Title: {title}" if title else "", f"Abstract: {abstract}" if abstract else ""] if part)
            if not combined:
                continue
            yield DocumentRecord(
                doc_id=str(row.get("id", index)),
                text=combined,
                metadata={"source_id": row.get("id"), "categories": categories},
            )


LOADER_REGISTRY = {
    "healthcaremagic": HealthCareMagicLoader,
    "msmarco": MSMARCOLoader,
    "nq": NQLoader,
    "fiqa": FiQALoader,
    "arxiv": ArxivLoader,
}


def get_dataset_loader(name: str) -> DatasetLoader:
    try:
        return LOADER_REGISTRY[name]()
    except KeyError as exc:
        available = ", ".join(sorted(LOADER_REGISTRY))
        raise KeyError(f"Unknown dataset loader '{name}'. Available loaders: {available}") from exc
