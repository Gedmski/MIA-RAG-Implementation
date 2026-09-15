from __future__ import annotations

import gc
import os
import random
import re
import time
from dataclasses import dataclass
from typing import Any

from .config import MIAConfig
from .types import DocumentRecord, DatasetSplit


@dataclass(frozen=True)
class ReconstructionDiagnostics:
    mask_accuracy: float
    correct_mask_count: int
    found_mask_count: int
    format_coverage: float
    response_len: int


@dataclass(frozen=True)
class MaskQualityDiagnostics:
    query_answer_leakage: float
    context_answer_coverage: float
    short_answer_rate: float
    common_answer_rate: float
    mask_count: int


@dataclass(frozen=True)
class RAGQueryResult:
    response: str
    retrieved_ids: list[str]
    context_ids: list[str]
    context: str
    raw_context: str
    retrieval_overlap_score: float


COMMON_MASK_ANSWERS = {
    "about",
    "after",
    "also",
    "been",
    "being",
    "between",
    "could",
    "does",
    "into",
    "many",
    "more",
    "most",
    "other",
    "over",
    "such",
    "than",
    "their",
    "there",
    "these",
    "they",
    "those",
    "through",
    "under",
    "using",
    "when",
    "where",
    "while",
    "would",
}


def _normalize_answer(value: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", " ", value.lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def _first_answer_candidate(value: str) -> str:
    candidate = value.strip()
    for separator in ["\n", ";", ",", "(", "[", " - ", " -- "]:
        if separator in candidate:
            candidate = candidate.split(separator, 1)[0]
    return _normalize_answer(candidate)


def _text_contains_answer(text: str, answer: str) -> bool:
    normalized_text = f" {_normalize_answer(text)} "
    normalized_answer = _normalize_answer(answer)
    return bool(normalized_answer and f" {normalized_answer} " in normalized_text)


def _primary_answers(ground_truth: dict[str, list[str]]) -> list[str]:
    answers: list[str] = []
    for valid_answers in ground_truth.values():
        if valid_answers:
            answers.append(valid_answers[0])
    return answers


def _all_answers(ground_truth: dict[str, list[str]]) -> list[str]:
    return [answer for valid_answers in ground_truth.values() for answer in valid_answers if answer]


def redact_answers_from_context(context: str, ground_truth: dict[str, list[str]]) -> str:
    redacted = context
    answers = sorted({_normalize_answer(answer) for answer in _all_answers(ground_truth)}, key=len, reverse=True)
    for answer in answers:
        if answer:
            redacted = re.sub(rf"(?<!\w){re.escape(answer)}(?!\w)", "[REDACTED]", redacted, flags=re.IGNORECASE)
    return redacted


def retrieval_overlap_score(masked_text: str, documents: list[Any]) -> float:
    query_without_masks = re.sub(r"\[MASK_\d+\]", " ", masked_text, flags=re.IGNORECASE)
    query_tokens = set(_normalize_answer(query_without_masks).split())
    if not query_tokens:
        return 0.0

    best = 0.0
    for document in documents:
        document_tokens = set(_normalize_answer(str(document.page_content)).split())
        if not document_tokens:
            continue
        best = max(best, len(query_tokens & document_tokens) / len(query_tokens | document_tokens))
    return float(best)


def select_context_documents(
    candidates: list[Any],
    *,
    context_mode: str,
    retriever_k: int,
    target_doc_id: str,
    ground_truth: dict[str, list[str]],
) -> list[Any]:
    if context_mode == "none":
        return []
    if context_mode != "leave_one_chunk_out":
        return candidates[:retriever_k]

    answers = _primary_answers(ground_truth)
    selected: list[Any] = []
    for document in candidates:
        parent_id = str(document.metadata.get("parent_id", document.metadata.get("id", "")))
        contains_answer = any(_text_contains_answer(str(document.page_content), answer) for answer in answers)
        if parent_id == str(target_doc_id) and contains_answer:
            continue
        selected.append(document)
        if len(selected) >= retriever_k:
            break
    return selected


def evaluate_mask_quality(
    masked_text: str,
    ground_truth: dict[str, list[str]],
    retrieved_context: str = "",
) -> MaskQualityDiagnostics:
    answers = [_normalize_answer(answer) for answer in _primary_answers(ground_truth)]
    answers = [answer for answer in answers if answer]
    if not answers:
        return MaskQualityDiagnostics(
            query_answer_leakage=0.0,
            context_answer_coverage=0.0,
            short_answer_rate=0.0,
            common_answer_rate=0.0,
            mask_count=0,
        )

    query_leaks = sum(1 for answer in answers if _text_contains_answer(masked_text, answer))
    context_hits = sum(1 for answer in answers if retrieved_context and _text_contains_answer(retrieved_context, answer))
    short_answers = sum(1 for answer in answers if len(answer) <= 4 or len(answer.split()) <= 0)
    common_answers = sum(1 for answer in answers if answer in COMMON_MASK_ANSWERS)
    total = len(answers)
    return MaskQualityDiagnostics(
        query_answer_leakage=query_leaks / total,
        context_answer_coverage=context_hits / total,
        short_answer_rate=short_answers / total,
        common_answer_rate=common_answers / total,
        mask_count=total,
    )


def _answer_occurrence_counts(words: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for word in words:
        key = _normalize_answer(word)
        if key:
            counts[key] = counts.get(key, 0) + 1
    return counts


def _is_non_leaking_mask_candidate(word: str, answer_counts: dict[str, int]) -> bool:
    key = _normalize_answer(word)
    return bool(key and answer_counts.get(key, 0) == 1)


def evaluate_reconstruction(response: str, ground_truth: dict[str, list[str]]) -> ReconstructionDiagnostics:
    if not ground_truth:
        return ReconstructionDiagnostics(
            mask_accuracy=0.0,
            correct_mask_count=0,
            found_mask_count=0,
            format_coverage=0.0,
            response_len=len(response),
        )

    response_lower = response.lower()
    correct = 0
    found = 0
    for mask_key, valid_answers in ground_truth.items():
        match = re.search(fr"{re.escape(mask_key).lower()}[:\s]+(.*?)(?:\n|$)", response_lower)
        if not match:
            continue
        found += 1
        predicted = _first_answer_candidate(match.group(1))
        valid = [_normalize_answer(answer) for answer in valid_answers]
        if any(answer and predicted == answer for answer in valid):
            correct += 1

    total_masks = len(ground_truth)
    return ReconstructionDiagnostics(
        mask_accuracy=correct / total_masks,
        correct_mask_count=correct,
        found_mask_count=found,
        format_coverage=found / total_masks,
        response_len=len(response),
    )


def _mean_metric(records: list[dict[str, Any]], key: str) -> float:
    if not records:
        return 0.0
    return float(sum(float(record.get(key, 0.0)) for record in records) / len(records))


def aggregate_attack_diagnostics(
    member_results: list[dict[str, Any]],
    non_member_results: list[dict[str, Any]],
    gamma: float,
) -> dict[str, float]:
    retrieved_members = [record for record in member_results if float(record.get("retrieval_hit", 0.0)) >= 1.0]
    generation_failures = [
        record for record in retrieved_members if float(record.get("mask_acc", 0.0)) < float(gamma)
    ]
    return {
        "member_mean_mask_accuracy": _mean_metric(member_results, "mask_acc"),
        "non_member_mean_mask_accuracy": _mean_metric(non_member_results, "mask_acc"),
        "member_mean_retrieval_overlap_score": _mean_metric(member_results, "retrieval_overlap_score"),
        "non_member_mean_retrieval_overlap_score": _mean_metric(non_member_results, "retrieval_overlap_score"),
        "member_context_retrieval_recall": _mean_metric(member_results, "context_retrieval_hit"),
        "member_mean_format_coverage": _mean_metric(member_results, "format_coverage"),
        "non_member_mean_format_coverage": _mean_metric(non_member_results, "format_coverage"),
        "member_exact_reconstruction_rate": _mean_metric(member_results, "exact_reconstruction"),
        "non_member_exact_reconstruction_rate": _mean_metric(non_member_results, "exact_reconstruction"),
        "member_query_answer_leakage_rate": _mean_metric(member_results, "query_answer_leakage"),
        "non_member_query_answer_leakage_rate": _mean_metric(non_member_results, "query_answer_leakage"),
        "member_context_answer_coverage": _mean_metric(member_results, "context_answer_coverage"),
        "non_member_context_answer_coverage": _mean_metric(non_member_results, "context_answer_coverage"),
        "member_raw_context_answer_coverage": _mean_metric(member_results, "raw_context_answer_coverage"),
        "non_member_raw_context_answer_coverage": _mean_metric(non_member_results, "raw_context_answer_coverage"),
        "mean_masks_per_sample": _mean_metric(member_results + non_member_results, "mask_count"),
        "member_short_answer_rate": _mean_metric(member_results, "short_answer_rate"),
        "non_member_short_answer_rate": _mean_metric(non_member_results, "short_answer_rate"),
        "member_common_answer_rate": _mean_metric(member_results, "common_answer_rate"),
        "non_member_common_answer_rate": _mean_metric(non_member_results, "common_answer_rate"),
        "generation_failure_rate": (
            float(len(generation_failures) / len(retrieved_members)) if retrieved_members else 0.0
        ),
    }


class MaskGenerator:
    def __init__(
        self,
        model_name: str = "gpt2",
        use_spelling: bool = True,
        seed: int = 42,
        avoid_query_answer_leakage: bool = True,
    ):
        import torch
        from transformers import AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoTokenizer

        self.torch = torch
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name).to(self.device).eval()
        self.use_spelling = use_spelling
        self.spelling_model = None
        self.spelling_tokenizer = None
        self.rng = random.Random(seed)
        self.avoid_query_answer_leakage = avoid_query_answer_leakage

        if self.use_spelling:
            try:
                self.spelling_tokenizer = AutoTokenizer.from_pretrained(
                    "oliverguhr/spelling-correction-english-base"
                )
                self.spelling_model = AutoModelForSeq2SeqLM.from_pretrained(
                    "oliverguhr/spelling-correction-english-base"
                ).to(self.device).eval()
            except Exception:
                self.use_spelling = False

    @staticmethod
    def is_valid_word(word: str) -> bool:
        if len(word) < 3:
            return False
        if not re.match(r"^[a-zA-Z]+$", word):
            return False
        stopwords = {
            "the",
            "and",
            "that",
            "with",
            "this",
            "from",
            "have",
            "was",
            "were",
            "which",
            "for",
            "are",
            "not",
            "but",
        }
        return word.lower() not in stopwords

    def correct_spelling(self, text_segment: str) -> str:
        if not self.use_spelling or not self.spelling_tokenizer or not self.spelling_model:
            return text_segment
        try:
            inputs = self.spelling_tokenizer(
                text_segment,
                return_tensors="pt",
                max_length=128,
                truncation=True,
            ).to(self.device)
            with self.torch.no_grad():
                outputs = self.spelling_model.generate(**inputs, max_length=128)
            return self.spelling_tokenizer.decode(outputs[0], skip_special_tokens=True)
        except Exception:
            return text_segment

    def generate_masks(self, text: str, num_masks: int = 5, strategy: str = "hard") -> tuple[str, dict[str, list[str]]]:
        words = text.split()
        if len(words) < num_masks * 2:
            return text, {}
        answer_counts = _answer_occurrence_counts(words)

        if strategy == "random":
            valid_indices = [
                i
                for i, word in enumerate(words)
                if self.is_valid_word(word)
                and (
                    not self.avoid_query_answer_leakage
                    or _is_non_leaking_mask_candidate(word, answer_counts)
                )
            ]
            selected_indices = self.rng.sample(valid_indices, min(len(valid_indices), num_masks))
        else:
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=1024).to(self.device)
            input_ids = inputs["input_ids"][0]

            with self.torch.no_grad():
                outputs = self.model(inputs["input_ids"], labels=inputs["input_ids"])
                logits = outputs.logits[0]

            word_scores: list[tuple[int, float]] = []
            current_token_idx = 0
            for index, word in enumerate(words):
                word_tokens = self.tokenizer.tokenize(" " + word)
                word_len = len(word_tokens)
                if current_token_idx + word_len >= len(input_ids):
                    break

                total_loss = 0.0
                valid_tokens = 0
                for token_index in range(current_token_idx, current_token_idx + word_len):
                    if token_index == 0:
                        continue
                    token_id = input_ids[token_index]
                    token_logits = logits[token_index - 1]
                    loss = self.torch.nn.functional.cross_entropy(token_logits.view(1, -1), token_id.view(1))
                    total_loss += loss.item()
                    valid_tokens += 1

                current_token_idx += word_len
                if self.is_valid_word(word):
                    word_scores.append((index, total_loss / max(1, valid_tokens)))

            word_scores.sort(key=lambda item: item[1], reverse=True)
            selected_indices = []
            for index, _ in word_scores:
                if len(selected_indices) >= num_masks:
                    break
                if self.avoid_query_answer_leakage and not _is_non_leaking_mask_candidate(words[index], answer_counts):
                    continue
                if any(abs(existing - index) <= 1 for existing in selected_indices):
                    continue
                selected_indices.append(index)

        selected_indices.sort()
        masked_words = list(words)
        ground_truth: dict[str, list[str]] = {}
        for mask_number, word_index in enumerate(selected_indices, start=1):
            original_word = words[word_index]
            answers = [original_word]
            if self.use_spelling:
                start_context = max(0, word_index - 2)
                corrected_chunk = self.correct_spelling(" ".join(words[start_context : word_index + 1]))
                corrected_word = corrected_chunk.split()[-1] if corrected_chunk.split() else ""
                corrected_clean = re.sub(r"[^\w]", "", corrected_word)
                original_clean = re.sub(r"[^\w]", "", original_word)
                if corrected_clean and corrected_clean.lower() != original_clean.lower():
                    answers.append(corrected_clean)
            mask_token = f"[MASK_{mask_number}]"
            masked_words[word_index] = mask_token
            ground_truth[mask_token] = answers
        return " ".join(masked_words), ground_truth


class OpenAIChatAdapter:
    def __init__(self, model_name: str, temperature: float):
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is required to run OpenAI-backed study configs.")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError("openai is required to run OpenAI-backed study configs.") from exc

        self.client = OpenAI()
        self.model_name = model_name
        self.temperature = temperature

    def invoke(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            temperature=self.temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        message = response.choices[0].message.content
        return message if isinstance(message, str) else ""


def build_llm(config: MIAConfig):
    provider = config.model_provider.lower()
    if provider == "openai":
        return OpenAIChatAdapter(model_name=config.llm_model_name, temperature=config.llm_temperature)

    if provider == "ollama":
        try:
            from langchain_ollama import OllamaLLM
        except ImportError:
            try:
                from langchain_community.llms import Ollama as OllamaLLM
            except ImportError as exc:
                raise ImportError("langchain-ollama or langchain-community is required for Ollama models.") from exc
        return OllamaLLM(model=config.llm_model_name, temperature=config.llm_temperature)

    raise ValueError(f"Unsupported model provider '{config.model_provider}'")


def _tpr_at_max_fpr(y_true: list[int], y_scores: list[float], max_fpr: float) -> float:
    positives = sum(1 for label in y_true if label == 1)
    negatives = sum(1 for label in y_true if label == 0)
    if positives == 0 or negatives == 0:
        return 0.0

    best_tpr = 0.0
    for threshold in sorted(set(y_scores), reverse=True):
        predicted = [1 if score >= threshold else 0 for score in y_scores]
        true_positive = sum(1 for label, pred in zip(y_true, predicted) if label == 1 and pred == 1)
        false_positive = sum(1 for label, pred in zip(y_true, predicted) if label == 0 and pred == 1)
        fpr = false_positive / negatives
        if fpr <= max_fpr:
            best_tpr = max(best_tpr, true_positive / positives)
    return best_tpr


def _roc_auc_score(y_true: list[int], y_scores: list[float]) -> float:
    positive_scores = [score for label, score in zip(y_true, y_scores) if label == 1]
    negative_scores = [score for label, score in zip(y_true, y_scores) if label == 0]
    if not positive_scores or not negative_scores:
        return 0.0

    wins = 0.0
    for positive in positive_scores:
        for negative in negative_scores:
            if positive > negative:
                wins += 1.0
            elif positive == negative:
                wins += 0.5
    return wins / (len(positive_scores) * len(negative_scores))


def _average_precision_score(y_true: list[int], y_scores: list[float]) -> float:
    positives = sum(1 for label in y_true if label == 1)
    if positives == 0:
        return 0.0

    ranked = sorted(zip(y_scores, y_true), key=lambda item: item[0], reverse=True)
    seen_positive = 0
    precision_sum = 0.0
    for rank, (_, label) in enumerate(ranked, start=1):
        if label == 1:
            seen_positive += 1
            precision_sum += seen_positive / rank
    return precision_sum / positives


def compute_membership_metrics(y_true: list[int], y_scores: list[float], gamma: float) -> dict[str, float]:
    y_pred = [1 if score >= gamma else 0 for score in y_scores]
    true_positive = sum(1 for label, pred in zip(y_true, y_pred) if label == 1 and pred == 1)
    true_negative = sum(1 for label, pred in zip(y_true, y_pred) if label == 0 and pred == 0)
    false_positive = sum(1 for label, pred in zip(y_true, y_pred) if label == 0 and pred == 1)
    false_negative = sum(1 for label, pred in zip(y_true, y_pred) if label == 1 and pred == 0)

    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    specificity = true_negative / (true_negative + false_positive) if true_negative + false_positive else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    accuracy = (true_positive + true_negative) / len(y_true) if y_true else 0.0
    balanced_accuracy = (recall + specificity) / 2 if len(set(y_true)) > 1 else 0.0
    auc_score = _roc_auc_score(y_true, y_scores)
    pr_auc = _average_precision_score(y_true, y_scores)
    return {
        "auc": float(auc_score),
        "pr_auc": float(pr_auc),
        "accuracy": float(accuracy),
        "balanced_accuracy": float(balanced_accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "tpr_at_1_fpr": _tpr_at_max_fpr(y_true, y_scores, 0.01),
        "tpr_at_5_fpr": _tpr_at_max_fpr(y_true, y_scores, 0.05),
    }


def select_decision_threshold(y_true: list[int], y_scores: list[float], fallback_gamma: float) -> float:
    if not y_scores or len(set(y_true)) < 2:
        return float(fallback_gamma)

    candidates = sorted(set(float(score) for score in y_scores) | {float(fallback_gamma)})
    best_threshold = float(fallback_gamma)
    best_f1 = -1.0
    best_balanced_accuracy = -1.0
    for threshold in candidates:
        metrics = compute_membership_metrics(y_true, y_scores, threshold)
        f1 = metrics["f1"]
        balanced_accuracy = metrics["balanced_accuracy"]
        if (
            f1 > best_f1
            or (f1 == best_f1 and balanced_accuracy > best_balanced_accuracy)
            or (
                f1 == best_f1
                and balanced_accuracy == best_balanced_accuracy
                and abs(threshold - fallback_gamma) < abs(best_threshold - fallback_gamma)
            )
        ):
            best_threshold = threshold
            best_f1 = f1
            best_balanced_accuracy = balanced_accuracy
    return float(best_threshold)


def bootstrap_auc_ci(
    y_true: list[int],
    y_scores: list[float],
    iterations: int,
    seed: int,
) -> tuple[float | None, float | None]:
    if iterations <= 0 or len(y_true) < 2 or len(set(y_true)) < 2:
        return None, None

    rng = random.Random(seed)
    pairs = list(zip(y_true, y_scores))
    values: list[float] = []
    for _ in range(iterations):
        sample = [rng.choice(pairs) for _ in pairs]
        sample_true = [label for label, _ in sample]
        if len(set(sample_true)) < 2:
            continue
        sample_scores = [score for _, score in sample]
        values.append(float(_roc_auc_score(sample_true, sample_scores)))

    if not values:
        return None, None
    values.sort()
    low_index = int(0.025 * (len(values) - 1))
    high_index = int(0.975 * (len(values) - 1))
    return values[low_index], values[high_index]


def chunk_document_text(text: str, chunk_chars: int | None, chunk_overlap: int = 0) -> list[str]:
    if not chunk_chars or chunk_chars <= 0 or len(text) <= chunk_chars:
        return [text]

    overlap = min(max(0, chunk_overlap), chunk_chars - 1)
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_chars)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = end - overlap
    return chunks or [text]


class RAGSystem:
    def __init__(self, config: MIAConfig, documents: list[DocumentRecord]):
        import torch

        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            from langchain_community.vectorstores import FAISS
            from langchain_core.documents import Document
        except ImportError:
            from langchain.embeddings import HuggingFaceEmbeddings
            from langchain.vectorstores import FAISS
            from langchain.docstore.document import Document

        self.torch = torch
        self.config = config
        self._document_cls = Document
        self.embeddings = HuggingFaceEmbeddings(
            model_name=config.embedding_model_name,
            encode_kwargs={"normalize_embeddings": True},
            model_kwargs={"device": "cuda" if torch.cuda.is_available() else "cpu"},
        )
        langchain_docs = []
        for document in documents:
            chunks = chunk_document_text(document.text, config.chunk_chars, config.chunk_overlap)
            for chunk_index, chunk_text in enumerate(chunks):
                chunk_id = document.doc_id if len(chunks) == 1 else f"{document.doc_id}::chunk-{chunk_index}"
                langchain_docs.append(
                    Document(
                        page_content=chunk_text,
                        metadata={
                            **document.metadata,
                            "id": chunk_id,
                            "parent_id": document.doc_id,
                            "chunk_index": chunk_index,
                            "chunk_count": len(chunks),
                        },
                    )
                )

        self.retrieval_candidate_k = min(
            len(langchain_docs),
            max(config.retriever_k, config.retriever_k * 4),
        )
        if config.retriever_type == "bm25":
            from langchain_community.retrievers import BM25Retriever

            self.vector_store = None
            self.retriever = BM25Retriever.from_documents(langchain_docs)
            self.retriever.k = self.retrieval_candidate_k
        else:
            self.vector_store = FAISS.from_documents(langchain_docs, self.embeddings)
            self.retriever = self.vector_store.as_retriever(search_kwargs={"k": self.retrieval_candidate_k})

        self.llm = build_llm(config)

    def query(
        self,
        masked_text: str,
        *,
        ground_truth: dict[str, list[str]] | None = None,
        target_doc_id: str = "",
    ) -> RAGQueryResult:
        ground_truth = ground_truth or {}
        candidates = list(self.retriever.invoke(masked_text))
        raw_docs = candidates[: self.config.retriever_k]
        context_docs = select_context_documents(
            candidates,
            context_mode=self.config.context_mode,
            retriever_k=self.config.retriever_k,
            target_doc_id=target_doc_id,
            ground_truth=ground_truth,
        )
        retrieved_ids = [
            str(document.metadata.get("parent_id", document.metadata.get("id", "")))
            for document in raw_docs
        ]
        context_ids = [
            str(document.metadata.get("parent_id", document.metadata.get("id", "")))
            for document in context_docs
        ]
        raw_context = "\n\n".join(str(document.page_content) for document in raw_docs)
        context = "\n\n".join(str(document.page_content) for document in context_docs)
        if self.config.context_mode == "answer_censored":
            context = redact_answers_from_context(context, ground_truth)

        context_instruction = (
            "Use your language knowledge to identify the original words. No retrieved context is available."
            if self.config.context_mode == "none"
            else "Use the provided context to identify the original words."
        )
        if "phi" in self.config.llm_model.lower():
            prompt = f"""Instruct: You are a helpful assistant. Below is a text with missing words marked as [MASK_N]. {context_instruction}

Context: {context[:2000]}...

Input Text: {masked_text}

Format your output strictly as:
[MASK_1]: <word>
[MASK_2]: <word>
"""
        else:
            prompt = f"""You are a helper. The following text contains masked words like [MASK_1]. {context_instruction}

Context:
{context}

Text with Masks:
{masked_text}

Please list the answers for each mask. Format:
[MASK_1]: answer_word
[MASK_2]: answer_word
"""
        response = self.llm.invoke(prompt)
        return RAGQueryResult(
            response=response,
            retrieved_ids=retrieved_ids,
            context_ids=context_ids,
            context=context,
            raw_context=raw_context,
            retrieval_overlap_score=retrieval_overlap_score(masked_text, raw_docs),
        )


class MIAAttacker:
    def __init__(self, config: MIAConfig):
        self.config = config
        self.mask_generator = MaskGenerator(
            model_name=config.proxy_model,
            use_spelling=config.use_spelling_correction,
            seed=config.seed,
            avoid_query_answer_leakage=config.avoid_query_answer_leakage,
        )

    @staticmethod
    def evaluate_correctness(response: str, ground_truth: dict[str, list[str]]) -> ReconstructionDiagnostics:
        return evaluate_reconstruction(response, ground_truth)

    def run_experiment(
        self,
        rag: RAGSystem,
        target_docs: list[DocumentRecord],
        is_member: bool,
        decision_threshold: float | None = None,
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        membership_label = 1 if is_member else 0
        threshold = self.config.gamma if decision_threshold is None else decision_threshold
        for document in target_docs:
            requested_masks = self.config.num_masks
            if self.config.mask_fraction is not None:
                requested_masks = max(1, round(len(document.text.split()) * self.config.mask_fraction))
            masked_text, ground_truth = self.mask_generator.generate_masks(
                document.text,
                num_masks=requested_masks,
                strategy=self.config.masking_strategy,
            )
            if not ground_truth:
                continue
            query_result = rag.query(
                masked_text,
                ground_truth=ground_truth,
                target_doc_id=str(document.doc_id),
            )
            diagnostics = self.evaluate_correctness(query_result.response, ground_truth)
            mask_quality = evaluate_mask_quality(masked_text, ground_truth, query_result.context)
            raw_mask_quality = evaluate_mask_quality(masked_text, ground_truth, query_result.raw_context)
            retrieval_hit = float(str(document.doc_id) in query_result.retrieved_ids)
            context_retrieval_hit = float(str(document.doc_id) in query_result.context_ids)
            results.append(
                {
                    "doc_id": str(document.doc_id),
                    "is_member": membership_label,
                    "mask_acc": diagnostics.mask_accuracy,
                    "correct_mask_count": diagnostics.correct_mask_count,
                    "found_mask_count": diagnostics.found_mask_count,
                    "format_coverage": diagnostics.format_coverage,
                    "retrieval_recall": retrieval_hit,
                    "retrieval_hit": retrieval_hit,
                    "context_retrieval_hit": context_retrieval_hit,
                    "retrieval_overlap_score": query_result.retrieval_overlap_score,
                    "response_len": diagnostics.response_len,
                    "exact_reconstruction": float(diagnostics.mask_accuracy >= 1.0),
                    "query_answer_leakage": mask_quality.query_answer_leakage,
                    "context_answer_coverage": mask_quality.context_answer_coverage,
                    "raw_context_answer_coverage": raw_mask_quality.context_answer_coverage,
                    "short_answer_rate": mask_quality.short_answer_rate,
                    "common_answer_rate": mask_quality.common_answer_rate,
                    "mask_count": mask_quality.mask_count,
                    "generation_failure": float(retrieval_hit >= 1.0 and diagnostics.mask_accuracy < threshold),
                }
            )
        return results


def _fingerprint_text(text: str) -> str:
    cleaned = re.sub(r"\W+", " ", text.lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def _word_shingles(text: str, width: int = 5) -> set[tuple[str, ...]]:
    words = _fingerprint_text(text).split()
    if len(words) < width:
        return {tuple(words)} if words else set()
    return {tuple(words[index : index + width]) for index in range(len(words) - width + 1)}


def _jaccard(left: set[tuple[str, ...]], right: set[tuple[str, ...]]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _non_member_overlap_stats(
    members: list[DocumentRecord],
    non_members: list[DocumentRecord],
    threshold: float = 0.8,
) -> dict[str, float]:
    if not non_members:
        return {
            "exact_duplicate_rate": 0.0,
            "near_duplicate_rate": 0.0,
            "max_similarity_mean": 0.0,
        }

    member_fingerprints = {_fingerprint_text(document.text) for document in members}
    member_shingles = [_word_shingles(document.text) for document in members]
    exact_duplicates = 0
    near_duplicates = 0
    max_similarities: list[float] = []

    for document in non_members:
        fingerprint = _fingerprint_text(document.text)
        if fingerprint in member_fingerprints:
            exact_duplicates += 1
        shingles = _word_shingles(document.text)
        max_similarity = max((_jaccard(shingles, member) for member in member_shingles), default=0.0)
        max_similarities.append(max_similarity)
        if max_similarity >= threshold:
            near_duplicates += 1

    total = len(non_members)
    return {
        "exact_duplicate_rate": exact_duplicates / total,
        "near_duplicate_rate": near_duplicates / total,
        "max_similarity_mean": sum(max_similarities) / total,
    }


def assess_split_contamination(split: DatasetSplit) -> dict[str, float]:
    eval_stats = _non_member_overlap_stats(split.members, split.eval_non_members)
    calibration_stats = _non_member_overlap_stats(split.members, split.calibration_non_members)
    return {
        "eval_non_member_exact_duplicate_rate": eval_stats["exact_duplicate_rate"],
        "eval_non_member_near_duplicate_rate": eval_stats["near_duplicate_rate"],
        "eval_non_member_max_similarity_mean": eval_stats["max_similarity_mean"],
        "calibration_non_member_exact_duplicate_rate": calibration_stats["exact_duplicate_rate"],
        "calibration_non_member_near_duplicate_rate": calibration_stats["near_duplicate_rate"],
        "calibration_non_member_max_similarity_mean": calibration_stats["max_similarity_mean"],
    }


def run_single_experiment(config: MIAConfig, split: DatasetSplit) -> dict[str, Any]:
    started = time.time()
    rag = RAGSystem(config, split.members)
    attacker = MIAAttacker(config)

    calibration_member_results = attacker.run_experiment(
        rag,
        split.calibration_members,
        is_member=True,
        decision_threshold=config.gamma,
    )
    calibration_non_member_results = attacker.run_experiment(
        rag,
        split.calibration_non_members,
        is_member=False,
        decision_threshold=config.gamma,
    )
    calibration_results = calibration_member_results + calibration_non_member_results

    effective_gamma = float(config.gamma)
    threshold_source = "configured"
    if config.calibrate_threshold and calibration_results:
        calibration_true = [item["is_member"] for item in calibration_results]
        calibration_scores = [item["mask_acc"] for item in calibration_results]
        if len(set(calibration_true)) > 1:
            effective_gamma = select_decision_threshold(calibration_true, calibration_scores, config.gamma)
            threshold_source = "calibration"
        else:
            threshold_source = "configured_insufficient_calibration"

    member_results = attacker.run_experiment(
        rag,
        split.eval_members,
        is_member=True,
        decision_threshold=effective_gamma,
    )
    non_member_results = attacker.run_experiment(
        rag,
        split.eval_non_members,
        is_member=False,
        decision_threshold=effective_gamma,
    )
    all_results = member_results + non_member_results

    if not all_results:
        raise RuntimeError("No results generated for experiment")

    y_true = [item["is_member"] for item in all_results]
    y_scores = [item["mask_acc"] for item in all_results]
    metrics = compute_membership_metrics(y_true, y_scores, effective_gamma)
    retrieval_scores = [item["retrieval_overlap_score"] for item in all_results]
    retrieval_only_auc = _roc_auc_score(y_true, retrieval_scores)
    retrieval_auc_ci_low, retrieval_auc_ci_high = bootstrap_auc_ci(
        y_true,
        retrieval_scores,
        config.bootstrap_iterations,
        config.seed + 17,
    )
    calibration_metrics = (
        compute_membership_metrics(
            [item["is_member"] for item in calibration_results],
            [item["mask_acc"] for item in calibration_results],
            effective_gamma,
        )
        if calibration_results
        else None
    )
    auc_ci_low, auc_ci_high = bootstrap_auc_ci(
        y_true,
        y_scores,
        config.bootstrap_iterations,
        config.seed,
    )
    retrieval_recalls = [item["retrieval_recall"] for item in member_results]
    avg_recall = sum(retrieval_recalls) / len(retrieval_recalls) if retrieval_recalls else 0.0
    diagnostics = aggregate_attack_diagnostics(member_results, non_member_results, effective_gamma)
    contamination = assess_split_contamination(split)
    runtime_seconds = time.time() - started

    if hasattr(rag, "torch") and rag.torch.cuda.is_available():
        rag.torch.cuda.empty_cache()
    del rag
    del attacker
    gc.collect()

    return {
        "study_name": config.study_name,
        "status": "success",
        "dataset": config.dataset_name,
        "dataset_loader": config.dataset_loader,
        "model_provider": config.model_provider,
        "llm_model": config.llm_model,
        "llm_model_name": config.llm_model_name,
        "model_family": config.model_family,
        "model_size_label": config.model_size_label,
        "model_params_b": config.model_params_b,
        "closed_weights": config.closed_weights,
        "embedding_model": config.embedding_model,
        "embedding_model_name": config.embedding_model_name,
        "retriever_type": config.retriever_type,
        "num_masks": config.num_masks,
        "retriever_k": config.retriever_k,
        "gamma": float(effective_gamma),
        "configured_gamma": float(config.gamma),
        "threshold_source": threshold_source,
        "calibrate_threshold": config.calibrate_threshold,
        "calibration_size": config.calibration_size,
        "bootstrap_iterations": config.bootstrap_iterations,
        "avoid_query_answer_leakage": config.avoid_query_answer_leakage,
        "context_mode": config.context_mode,
        "mask_fraction": config.mask_fraction,
        "chunk_chars": config.chunk_chars,
        "chunk_overlap": config.chunk_overlap,
        "index_size": config.index_size,
        "eval_size": config.eval_size,
        "member_samples": len(member_results),
        "non_member_samples": len(non_member_results),
        "calibration_member_samples": len(calibration_member_results),
        "calibration_non_member_samples": len(calibration_non_member_results),
        "auc": metrics["auc"],
        "auc_ci_low": auc_ci_low,
        "auc_ci_high": auc_ci_high,
        "pr_auc": metrics["pr_auc"],
        "retrieval_only_auc": retrieval_only_auc,
        "retrieval_only_auc_ci_low": retrieval_auc_ci_low,
        "retrieval_only_auc_ci_high": retrieval_auc_ci_high,
        "balanced_accuracy": metrics["balanced_accuracy"],
        "tpr_at_1_fpr": metrics["tpr_at_1_fpr"],
        "tpr_at_5_fpr": metrics["tpr_at_5_fpr"],
        "accuracy": metrics["accuracy"],
        "precision": metrics["precision"],
        "recall": metrics["recall"],
        "f1": metrics["f1"],
        "calibration_auc": calibration_metrics["auc"] if calibration_metrics else None,
        "calibration_pr_auc": calibration_metrics["pr_auc"] if calibration_metrics else None,
        "calibration_f1": calibration_metrics["f1"] if calibration_metrics else None,
        "retrieval_recall": float(avg_recall),
        "context_retrieval_recall": diagnostics["member_context_retrieval_recall"],
        "member_mean_mask_accuracy": diagnostics["member_mean_mask_accuracy"],
        "non_member_mean_mask_accuracy": diagnostics["non_member_mean_mask_accuracy"],
        "member_mean_retrieval_overlap_score": diagnostics["member_mean_retrieval_overlap_score"],
        "non_member_mean_retrieval_overlap_score": diagnostics["non_member_mean_retrieval_overlap_score"],
        "member_mean_format_coverage": diagnostics["member_mean_format_coverage"],
        "non_member_mean_format_coverage": diagnostics["non_member_mean_format_coverage"],
        "member_exact_reconstruction_rate": diagnostics["member_exact_reconstruction_rate"],
        "non_member_exact_reconstruction_rate": diagnostics["non_member_exact_reconstruction_rate"],
        "member_query_answer_leakage_rate": diagnostics["member_query_answer_leakage_rate"],
        "non_member_query_answer_leakage_rate": diagnostics["non_member_query_answer_leakage_rate"],
        "member_context_answer_coverage": diagnostics["member_context_answer_coverage"],
        "non_member_context_answer_coverage": diagnostics["non_member_context_answer_coverage"],
        "member_raw_context_answer_coverage": diagnostics["member_raw_context_answer_coverage"],
        "non_member_raw_context_answer_coverage": diagnostics["non_member_raw_context_answer_coverage"],
        "mean_masks_per_sample": diagnostics["mean_masks_per_sample"],
        "member_short_answer_rate": diagnostics["member_short_answer_rate"],
        "non_member_short_answer_rate": diagnostics["non_member_short_answer_rate"],
        "member_common_answer_rate": diagnostics["member_common_answer_rate"],
        "non_member_common_answer_rate": diagnostics["non_member_common_answer_rate"],
        "generation_failure_rate": diagnostics["generation_failure_rate"],
        **contamination,
        "runtime_seconds": round(runtime_seconds, 4),
        "failure_reason": "",
        "config_repr": config.compat_repr(),
        "sample_results": all_results,
    }
