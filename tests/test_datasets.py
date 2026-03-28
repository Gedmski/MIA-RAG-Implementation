from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mia_rag.config import DatasetSpec
from mia_rag.datasets import prepare_dataset_split
from mia_rag.datasets.loaders import ArxivLoader, HealthCareMagicLoader
from mia_rag.types import DocumentRecord


def test_prepare_dataset_split_is_deterministic():
    documents = [
        DocumentRecord(doc_id=str(index), text=f"Document {index} " * 30, metadata={})
        for index in range(20)
    ]
    split_a = prepare_dataset_split(documents, index_size=10, eval_size=4, seed=7)
    split_b = prepare_dataset_split(documents, index_size=10, eval_size=4, seed=7)
    assert [document.doc_id for document in split_a.members] == [document.doc_id for document in split_b.members]
    assert len(split_a.eval_members) == 4
    assert len(split_a.eval_non_members) == 4


def test_arxiv_loader_filters_requested_category(monkeypatch):
    loader = ArxivLoader()
    spec = DatasetSpec(
        name="arxiv",
        loader="arxiv",
        dataset_id="unused",
        split="train",
        category="cs.CL",
        index_size=1,
        eval_size=0,
        min_chars=10,
        max_chars=200,
    )

    def fake_split(_spec):
        return [
            {"id": "1", "title": "Paper A", "abstract": "Natural language processing abstract", "categories": "cs.CL"},
            {"id": "2", "title": "Paper B", "abstract": "Vision abstract", "categories": "cs.CV"},
        ]

    monkeypatch.setattr(loader, "load_split", fake_split)
    documents = loader.load_documents(spec)
    assert len(documents) == 1
    assert documents[0].doc_id == "1"


def test_healthcaremagic_loader_supports_text_field(monkeypatch):
    loader = HealthCareMagicLoader()
    spec = DatasetSpec(
        name="healthcaremagic",
        loader="healthcaremagic",
        dataset_id="unused",
        split="train",
        index_size=1,
        eval_size=0,
        min_chars=10,
        max_chars=200,
        loader_options={"text_fields": ["text"]},
    )

    def fake_split(_spec):
        return [
            {"id": "h1", "text": "Patient presents with a long enough medical note for validation."},
        ]

    monkeypatch.setattr(loader, "load_split", fake_split)
    documents = loader.load_documents(spec)
    assert len(documents) == 1
    assert documents[0].doc_id == "h1"


def test_arxiv_loader_keeps_rows_without_category_metadata(monkeypatch):
    loader = ArxivLoader()
    spec = DatasetSpec(
        name="arxiv",
        loader="arxiv",
        dataset_id="unused",
        split="train",
        category="Computation and Language",
        index_size=1,
        eval_size=0,
        min_chars=10,
        max_chars=200,
        loader_options={
            "title_fields": ["Titles"],
            "abstract_fields": ["Abstracts"],
            "category_fields": ["Categories"],
        },
    )

    def fake_split(_spec):
        return [
            {"id": "1", "Titles": "Paper A", "Abstracts": "A sufficiently long abstract for testing."},
        ]

    monkeypatch.setattr(loader, "load_split", fake_split)
    documents = loader.load_documents(spec)
    assert len(documents) == 1
    assert documents[0].doc_id == "1"
