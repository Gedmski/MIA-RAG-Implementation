from __future__ import annotations

import sys
from pathlib import Path
import types


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mia_rag.config import MIAConfig
from mia_rag.pipeline import (
    OpenAIChatAdapter,
    aggregate_attack_diagnostics,
    build_llm,
    compute_membership_metrics,
    evaluate_reconstruction,
)


def _base_config(provider: str, model_name: str) -> MIAConfig:
    return MIAConfig(
        study_name="baseline",
        model_provider=provider,
        llm_model=model_name,
        llm_model_name=model_name,
        model_family=None,
        model_size_label=None,
        model_params_b=None,
        closed_weights=None,
        embedding_model="mini",
        embedding_model_name="sentence-transformers/all-MiniLM-L6-v2",
        dataset_name="sample",
        dataset_loader="healthcaremagic",
        dataset_id="sample",
        dataset_config=None,
        dataset_split="train",
        dataset_streaming=False,
        dataset_category=None,
        dataset_loader_options={},
        proxy_model="gpt2",
        num_masks=5,
        retriever_k=3,
        gamma=0.5,
        masking_strategy="hard",
        use_spelling_correction=True,
        retriever_type="faiss",
        index_size=50,
        eval_size=10,
        min_chars=10,
        max_chars=200,
        seed=42,
        llm_temperature=0.0,
    )


def test_compute_membership_metrics_respects_gamma_threshold():
    metrics = compute_membership_metrics(
        y_true=[1, 1, 0, 0],
        y_scores=[0.9, 0.6, 0.7, 0.1],
        gamma=0.7,
    )
    assert round(metrics["auc"], 4) == 0.75
    assert round(metrics["accuracy"], 4) == 0.75
    assert round(metrics["precision"], 4) == 0.5
    assert round(metrics["recall"], 4) == 0.5
    assert round(metrics["f1"], 4) == 0.5


def test_build_llm_selects_openai_provider(monkeypatch):
    class FakeOpenAIClient:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(create=lambda **_: types.SimpleNamespace(
                    choices=[types.SimpleNamespace(message=types.SimpleNamespace(content="ok"))]
                ))
            )

    fake_module = types.ModuleType("openai")
    fake_module.OpenAI = FakeOpenAIClient
    monkeypatch.setitem(sys.modules, "openai", fake_module)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    llm = build_llm(_base_config(provider="openai", model_name="gpt-4o-mini"))
    assert isinstance(llm, OpenAIChatAdapter)
    assert llm.invoke("hello") == "ok"


def test_build_llm_selects_ollama_provider(monkeypatch):
    class FakeOllamaLLM:
        def __init__(self, model: str, temperature: float):
            self.model = model
            self.temperature = temperature

        def invoke(self, prompt: str) -> str:
            return prompt

    fake_module = types.ModuleType("langchain_ollama")
    fake_module.OllamaLLM = FakeOllamaLLM
    monkeypatch.setitem(sys.modules, "langchain_ollama", fake_module)

    llm = build_llm(_base_config(provider="ollama", model_name="llama3"))
    assert isinstance(llm, FakeOllamaLLM)
    assert llm.model == "llama3"
    assert llm.temperature == 0.0


def test_evaluate_reconstruction_returns_structured_diagnostics():
    diagnostics = evaluate_reconstruction(
        response="[MASK_1]: insulin\n[MASK_2]: pancreas",
        ground_truth={
            "[MASK_1]": ["insulin"],
            "[MASK_2]": ["pancreas"],
            "[MASK_3]": ["glucose"],
        },
    )
    assert round(diagnostics.mask_accuracy, 4) == 0.6667
    assert diagnostics.correct_mask_count == 2
    assert diagnostics.found_mask_count == 2
    assert round(diagnostics.format_coverage, 4) == 0.6667
    assert diagnostics.response_len > 0


def test_aggregate_attack_diagnostics_tracks_generation_failures():
    member_results = [
        {"mask_acc": 1.0, "format_coverage": 1.0, "exact_reconstruction": 1.0, "retrieval_hit": 1.0},
        {"mask_acc": 0.4, "format_coverage": 0.5, "exact_reconstruction": 0.0, "retrieval_hit": 1.0},
    ]
    non_member_results = [
        {"mask_acc": 0.2, "format_coverage": 0.5, "exact_reconstruction": 0.0, "retrieval_hit": 0.0},
        {"mask_acc": 0.0, "format_coverage": 0.0, "exact_reconstruction": 0.0, "retrieval_hit": 0.0},
    ]
    diagnostics = aggregate_attack_diagnostics(member_results, non_member_results, gamma=0.5)
    assert round(diagnostics["member_mean_mask_accuracy"], 4) == 0.7
    assert round(diagnostics["non_member_mean_mask_accuracy"], 4) == 0.1
    assert round(diagnostics["member_mean_format_coverage"], 4) == 0.75
    assert round(diagnostics["generation_failure_rate"], 4) == 0.5
