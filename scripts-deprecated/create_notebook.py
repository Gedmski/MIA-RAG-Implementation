
import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

text_intro = """# Mask-Based Membership Inference Attack (MIA) on RAG

This notebook implements a Membership Inference Attack against a local RAG system.
It follows the specifications to:
1.  Generate synthetic data (Members vs Non-Members).
2.  Build a RAG system using **Ollama** (Llama3) and **FAISS**.
3.  Use a Proxy Model (**GPT-2**) to generate difficult masks.
4.  Attack the RAG by asking it to fill in the masks.
5.  Evaluate success using AUC-ROC.

## Prerequisites
- Ollama running locally (`ollama serve`).
- Models pulled: `ollama pull llama3`, `ollama pull nomic-embed-text` (if used).
"""

code_imports = """
import os
import random
import numpy as np
import pandas as pd
import json
import torch
import torch.nn.functional as F
from typing import List, Dict, Tuple, Optional
from tqdm import tqdm
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc, roc_auc_score
import re

# LangChain & RAG imports
import langchain
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Try modern imports first (LangChain v0.1+)
try:
    from langchain_community.llms import Ollama
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    # Legacy Fallbacks
    try:
        from langchain.llms import Ollama
        from langchain.embeddings import HuggingFaceEmbeddings
        from langchain.vectorstores import FAISS
        from langchain.text_splitter import RecursiveCharacterTextSplitter
    except ImportError:
        # Last resort for some community packages
        from langchain_community.chat_models import ChatOllama as Ollama
        pass

# Transformers for Proxy Model
from transformers import GPT2LMHeadModel, GPT2Tokenizer, AutoModelForCausalLM, AutoTokenizer
"""

code_config = """
# Configuration for Ablation Studies
class MIAConfig:
    def __init__(self, 
                 llm_model: str = "llama3",
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                 retriever_type: str = "faiss",
                 dataset_type: str = "general",
                 proxy_model: str = "gpt2",
                 num_masks: int = 5,
                 top_k_retrieval: int = 3):
        self.llm_model = llm_model
        self.embedding_model = embedding_model
        self.retriever_type = retriever_type
        self.dataset_type = dataset_type
        self.proxy_model = proxy_model
        self.num_masks = num_masks
        self.top_k_retrieval = top_k_retrieval

    def __repr__(self):
        return f"Config(LLM={self.llm_model}, Embed={self.embedding_model}, Retriever={self.retriever_type}, Dataset={self.dataset_type})"
"""

code_data = """
# --- Step 1: Data Preparation ---
def generate_synthetic_data(dataset_type: str = "general") -> List[str]:
    # ... (Please refer to full script for the dictionary) ...
    # For brevity in this notebook cell, we use the implementation from the script directly or re-define here.
    # Re-defining core lists:
    general_topics = [
        "Photosynthesis is the process used by plants, algae and certain bacteria to harness energy from sunlight and turn it into chemical energy.",
        "The history of quantum computing began in the early 1980s when physicist Paul Benioff proposed a quantum mechanical model of the Turing machine.",
        "The Great Wall of China is a series of fortifications that were built across the historical northern borders of ancient Chinese states.",
        "Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to the natural intelligence displayed by animals including humans.",
        "The theory of relativity usually encompasses two interrelated theories by Albert Einstein: special relativity and general relativity.",
        "DNA replication is the biological process of producing two identical replicas of DNA from one original DNA molecule.",
        "The industrial revolution was the transition to new manufacturing processes in Great Britain, continental Europe, and the United States.",
        "Blockchain is a decentralized, distributed and public digital ledger that is used to record transactions across many computers.",
        "Climate change describes global warming—the ongoing increase in global average temperature—and its effects on Earth's climate system.",
        "The human brain is the central organ of the human nervous system, and with the spinal cord makes up the central nervous system.",
        "Antibiotics are medications used to treat bacterial infections. They work by killing bacteria or preventing them from reproducing.",
        "The Internet of Things (IoT) describes the network of physical objects identifying themselves to other devices and servers over the Internet."
    ]
    # ... (other lists omitted for brevity but assumed present in robust implementation) ...
    return general_topics * 2 # Simple duplication for demo

def prepare_datasets(texts: List[str], split_ratio: float = 0.8) -> Tuple[List[str], List[str]]:
    random.seed(42)
    random.shuffle(texts)
    split_idx = int(len(texts) * split_ratio)
    member_set = texts[:split_idx]
    non_member_set = texts[split_idx:]
    return member_set, non_member_set
"""

code_proxy = """
# --- Step 2: Proxy Model (Mask Generation) ---
class ProxyModel:
    def __init__(self, model_name: str = "gpt2", device: str = None):
        self.model_name = model_name
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Loading Proxy Model: {model_name} on {self.device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name).to(self.device)
        self.model.eval()

    def rank_words(self, text: str, num_masks: int = 5) -> Tuple[str, Dict[str, str]]:
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        input_ids = inputs["input_ids"]
        
        with torch.no_grad():
            outputs = self.model(**inputs, labels=input_ids)
            logits = outputs.logits
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = input_ids[..., 1:].contiguous()
            loss_fct = torch.nn.CrossEntropyLoss(reduction='none')
            loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
            
        top_k_indices = torch.argsort(loss, descending=True)[:num_masks]
        top_k_indices = top_k_indices + 1 
        top_k_indices = top_k_indices.cpu().numpy().tolist()
        
        masked_tokens = list(input_ids[0].cpu().numpy())
        ground_truth = {}
        token_strs = [self.tokenizer.decode([t]) for t in masked_tokens]
        
        for i, idx in enumerate(top_k_indices):
            if idx < len(token_strs):
                original = token_strs[idx]
                token_strs[idx] = f" [MASK_{i+1}]"
                ground_truth[f"[MASK_{i+1}]"] = original.strip()
            
        masked_text = "".join(token_strs)
        return masked_text, ground_truth
"""

code_rag = """
# --- Step 3: RAG System ---
class RAGSystem:
    def __init__(self, config: MIAConfig, member_texts: List[str]):
        self.config = config
        print(f"Initializing RAG with LLM={config.llm_model} and Embed={config.embedding_model}")
        
        self.embeddings = HuggingFaceEmbeddings(model_name=config.embedding_model)
        
        print("Building Vector Store...")
        self.vector_store = FAISS.from_texts(member_texts, self.embeddings)
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": config.top_k_retrieval})
        
        self.llm = Ollama(model=config.llm_model, temperature=0, num_predict=50)
        
        template = \"\"\"You are a helpful assistant. Use the following pieces of context to fill in the missing [MASK_N] placeholders in the text.
        
        Context:
        {context}
        
        Please provide the original words for the placeholders in the format:
        [MASK_1]: answer
        [MASK_2]: answer
        
        Text to fill:
        {question}
        \"\"\"
        self.qa_prompt = PromptTemplate(template=template, input_variables=["context", "question"])
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={"prompt": self.qa_prompt}
        )

    def query(self, masked_text: str) -> str:
        return self.qa_chain.invoke(masked_text)['result']
"""

code_attack = """
# --- Step 4 & 5: Attack & Evaluation ---
class MIAAttacker:
    def __init__(self, config: MIAConfig):
        self.config = config
        self.proxy = ProxyModel(model_name=config.proxy_model)
    
    def evaluate_response(self, response: str, ground_truth: Dict[str, str]) -> float:
        correct_count = 0
        total_masks = len(ground_truth)
        if total_masks == 0: return 0.0
        response_lower = response.lower()
        for mask_key, answer in ground_truth.items():
            if mask_key.lower() in response_lower:
                part = response_lower.split(mask_key.lower())[1]
                line = part.split('\\n')[0]
                if answer.lower().strip() in line:
                    correct_count += 1
        return correct_count / total_masks

    def run_attack(self, rag_system: RAGSystem, documents: List[str], is_member: bool) -> List[Dict]:
        results = []
        label = 1 if is_member else 0
        print(f"Running attack on {'Members' if is_member else 'Non-Members'}...")
        for doc in tqdm(documents):
            masked_text, ground_truth = self.proxy.rank_words(doc, num_masks=self.config.num_masks)
            try:
                response = rag_system.query(masked_text)
                accuracy = self.evaluate_response(response, ground_truth)
                results.append({
                    "text_preview": doc[:30],
                    "is_member": label,
                    "accuracy": accuracy,
                    "ground_truth": ground_truth,
                    "response_preview": response[:50]
                })
            except Exception as e:
                pass
        return results

def plot_roc_curve(y_true, y_scores, title="ROC Curve"):
    fpr, tpr, _ = roc_curve(y_true, y_scores)
    roc_auc = auc(fpr, tpr)
    plt.figure()
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(title)
    plt.legend(loc="lower right")
    plt.show()
    return roc_auc
"""

code_main = """
# --- Main Execution ---
def run_experiment(config: MIAConfig):
    print(f"--- Starting Experiment: {config} ---")
    data = generate_synthetic_data(config.dataset_type)
    members, non_members = prepare_datasets(data)
    rag = RAGSystem(config, members)
    attacker = MIAAttacker(config)
    results_member = attacker.run_attack(rag, members, is_member=True)
    results_non_member = attacker.run_attack(rag, non_members, is_member=False)
    all_results = results_member + results_non_member
    y_true = [r['is_member'] for r in all_results]
    y_scores = [r['accuracy'] for r in all_results]
    auc_score = plot_roc_curve(y_true, y_scores, title=f"ROC - {config.llm_model}")
    return all_results, auc_score

# Run
if __name__ == "__main__":
    config = MIAConfig(llm_model="llama3", dataset_type="general")
    run_experiment(config)
"""

nb['cells'] = [
    nbf.v4.new_code_cell("%pip install langchain langchain-community langchain-huggingface faiss-cpu transformers torch scikit-learn matplotlib ipykernel"),
    nbf.v4.new_markdown_cell(text_intro),
    nbf.v4.new_code_cell(code_imports),
    nbf.v4.new_code_cell(code_config),
    nbf.v4.new_code_cell(code_data),
    nbf.v4.new_code_cell(code_proxy),
    nbf.v4.new_code_cell(code_rag),
    nbf.v4.new_code_cell(code_attack),
    nbf.v4.new_code_cell(code_main)
]

with open('MIA_RAG_Attack.ipynb', 'w') as f:
    nbf.write(nb, f)

print("Notebook generated successfully.")
