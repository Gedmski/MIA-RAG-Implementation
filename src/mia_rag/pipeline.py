from __future__ import annotations

import gc
import os
import re
import time
from typing import Any

from .config import MIAConfig
from .types import DocumentRecord, DatasetSplit


class MaskGenerator:
    def __init__(self, model_name: str = "gpt2", use_spelling: bool = True):
        import torch
        from transformers import AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoTokenizer

        self.torch = torch
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name).to(self.device).eval()
        self.use_spelling = use_spelling
        self.spelling_model = None
        self.spelling_tokenizer = None

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
        import random

        words = text.split()
        if len(words) < num_masks * 2:
            return text, {}

        if strategy == "random":
            valid_indices = [i for i, word in enumerate(words) if self.is_valid_word(word)]
            selected_indices = random.sample(valid_indices, min(len(valid_indices), num_masks))
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


def compute_membership_metrics(y_true: list[int], y_scores: list[float], gamma: float) -> dict[str, float]:
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score

    y_pred = [1 if score >= gamma else 0 for score in y_scores]
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        average="binary",
        zero_division=0,
    )
    auc_score = roc_auc_score(y_true, y_scores) if len(set(y_true)) > 1 else 0.0
    return {
        "auc": float(auc_score),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
    }


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
        langchain_docs = [
            Document(page_content=document.text, metadata={"id": document.doc_id, **document.metadata})
            for document in documents
        ]

        if config.retriever_type == "bm25":
            from langchain_community.retrievers import BM25Retriever

            self.vector_store = None
            self.retriever = BM25Retriever.from_documents(langchain_docs)
            self.retriever.k = config.retriever_k
        else:
            self.vector_store = FAISS.from_documents(langchain_docs, self.embeddings)
            self.retriever = self.vector_store.as_retriever(search_kwargs={"k": config.retriever_k})

        self.llm = build_llm(config)

    def query(self, masked_text: str) -> tuple[str, list[str]]:
        docs = self.retriever.invoke(masked_text)
        retrieved_ids = [str(document.metadata.get("id", "")) for document in docs]
        context = "\n\n".join(document.page_content for document in docs)
        if "phi" in self.config.llm_model.lower():
            prompt = f"""Instruct: You are a helpful assistant. Below is a text with missing words marked as [MASK_N]. Use the provided Context to identify the missing words.

Context: {context[:2000]}...

Input Text: {masked_text}

Format your output strictly as:
[MASK_1]: <word>
[MASK_2]: <word>
"""
        else:
            prompt = f"""You are a helper. The following text contains masked words like [MASK_1]. Using the context provided, identify the original words.

Context:
{context}

Text with Masks:
{masked_text}

Please list the answers for each mask. Format:
[MASK_1]: answer_word
[MASK_2]: answer_word
"""
        response = self.llm.invoke(prompt)
        return response, retrieved_ids


class MIAAttacker:
    def __init__(self, config: MIAConfig):
        self.config = config
        self.mask_generator = MaskGenerator(
            model_name=config.proxy_model,
            use_spelling=config.use_spelling_correction,
        )

    @staticmethod
    def evaluate_correctness(response: str, ground_truth: dict[str, list[str]]) -> float:
        if not ground_truth:
            return 0.0
        response_lower = response.lower()
        correct = 0
        for mask_key, valid_answers in ground_truth.items():
            match = re.search(fr"{re.escape(mask_key).lower()}[:\s]+(.*?)(?:\n|$)", response_lower)
            if not match:
                continue
            predicted_raw = match.group(1)
            predicted_words = re.split(r"\W+", predicted_raw)
            valid = [answer.lower().strip() for answer in valid_answers]
            if any(answer in predicted_words or answer in predicted_raw for answer in valid):
                correct += 1
        return correct / len(ground_truth)

    def run_experiment(self, rag: RAGSystem, target_docs: list[DocumentRecord], is_member: bool) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        membership_label = 1 if is_member else 0
        for document in target_docs:
            masked_text, ground_truth = self.mask_generator.generate_masks(
                document.text,
                num_masks=self.config.num_masks,
                strategy=self.config.masking_strategy,
            )
            if not ground_truth:
                continue
            response, retrieved_ids = rag.query(masked_text)
            mask_accuracy = self.evaluate_correctness(response, ground_truth)
            retrieval_hit = float(str(document.doc_id) in retrieved_ids) if is_member else 0.0
            results.append(
                {
                    "is_member": membership_label,
                    "mask_acc": mask_accuracy,
                    "retrieval_recall": retrieval_hit,
                    "response_len": len(response),
                }
            )
        return results


def run_single_experiment(config: MIAConfig, split: DatasetSplit) -> dict[str, Any]:
    started = time.time()
    rag = RAGSystem(config, split.members)
    attacker = MIAAttacker(config)
    member_results = attacker.run_experiment(rag, split.eval_members, is_member=True)
    non_member_results = attacker.run_experiment(rag, split.eval_non_members, is_member=False)
    all_results = member_results + non_member_results

    if not all_results:
        raise RuntimeError("No results generated for experiment")

    y_true = [item["is_member"] for item in all_results]
    y_scores = [item["mask_acc"] for item in all_results]
    metrics = compute_membership_metrics(y_true, y_scores, config.gamma)
    retrieval_recalls = [item["retrieval_recall"] for item in member_results]
    avg_recall = sum(retrieval_recalls) / len(retrieval_recalls) if retrieval_recalls else 0.0
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
        "embedding_model": config.embedding_model,
        "embedding_model_name": config.embedding_model_name,
        "retriever_type": config.retriever_type,
        "num_masks": config.num_masks,
        "retriever_k": config.retriever_k,
        "gamma": float(config.gamma),
        "index_size": config.index_size,
        "eval_size": config.eval_size,
        "member_samples": len(member_results),
        "non_member_samples": len(non_member_results),
        "auc": metrics["auc"],
        "accuracy": metrics["accuracy"],
        "precision": metrics["precision"],
        "recall": metrics["recall"],
        "f1": metrics["f1"],
        "retrieval_recall": float(avg_recall),
        "runtime_seconds": round(runtime_seconds, 4),
        "failure_reason": "",
        "config_repr": config.compat_repr(),
    }
