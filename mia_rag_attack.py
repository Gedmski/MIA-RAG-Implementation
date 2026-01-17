
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
from sklearn.metrics import roc_curve, auc, roc_auc_score, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import re
from datetime import datetime
import time

# Datasets
try:
    from datasets import load_dataset
except ImportError:
    print("Warning: 'datasets' library not found. Please install: pip install datasets")
    load_dataset = None


# LangChain & RAG imports
import langchain
import requests
import json
import sys
from langchain_core.documents import Document
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_core.prompts import PromptTemplate

# Try modern imports first (LangChain v0.1+)
try:
    from langchain_ollama import OllamaLLM
    OllamaClass = OllamaLLM
except ImportError:
    try:
        from langchain_community.llms import Ollama
        OllamaClass = Ollama
    except ImportError:
        from langchain.llms import Ollama
        OllamaClass = Ollama

try:
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    # Legacy Fallbacks
    from langchain.embeddings import HuggingFaceEmbeddings
    from langchain.vectorstores import FAISS
    from langchain.text_splitter import RecursiveCharacterTextSplitter


try:
    from langchain_community.retrievers import BM25Retriever
except ImportError:
    try:
        from langchain.retrievers import BM25Retriever
    except ImportError:
        BM25Retriever = None


def ensure_ollama_model(model_name: str, base_url: str = "http://localhost:11434"):
    """
    Checks if the specified model exists in Ollama. If not, attempts to pull it.
    """
    print(f"Checking for Ollama model: {model_name}...")
    try:
        # 1. List local models
        response = requests.get(f"{base_url}/api/tags")
        if response.status_code == 200:
            models = [m['name'] for m in response.json().get('models', [])]
            # Handle tags like 'llama3:latest' vs 'llama3'
            if model_name in models or f"{model_name}:latest" in models:
                print(f"Model '{model_name}' is ready.")
                return True
            
            # Check if any version of the model exists (e.g. user asked for llama3, we have llama3:8b)
            # Simple substring check might be risky but helpful
            for m in models:
                if model_name in m:
                    print(f"Found related model '{m}', assuming it covers '{model_name}' request or ignoring.")
                    # We usually want exact match or we pull. 
                    # If user asks for 'llama3', 'llama3:latest' is the target.
                    if m == f"{model_name}:latest":
                         print(f"Model '{model_name}' is ready (found {m}).")
                         return True

        # 2. Pull model if missing
        print(f"Model '{model_name}' not found locally. Pulling from registry (this may take a while)...")
        
        # Streaming pull to show progress
        pull_resp = requests.post(f"{base_url}/api/pull", json={"name": model_name}, stream=True)
        if pull_resp.status_code == 200:
            for line in pull_resp.iter_lines():
                if line:
                    data = json.loads(line.decode('utf-8'))
                    status = data.get('status', '')
                    completed = data.get('completed', 0)
                    total = data.get('total', 0)
                    if total > 0:
                        percent = (completed / total) * 100
                        sys.stdout.write(f"\rPulling {model_name}: {status} - {percent:.1f}%")
                        sys.stdout.flush()
                    else:
                        sys.stdout.write(f"\rPulling {model_name}: {status}")
                        sys.stdout.flush()
            print(f"\nModel '{model_name}' pulled successfully.")
            return True
        else:
            print(f"Failed to pull model '{model_name}'. Status: {pull_resp.status_code}")
            return False
            
    except Exception as e:
        print(f"Error checking/pulling Ollama model: {e}")
        return False

# Transformers for Proxy Model
from transformers import GPT2LMHeadModel, GPT2Tokenizer, AutoModelForCausalLM, AutoTokenizer


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

# --- Step 1: Data Preparation ---
def generate_synthetic_data(dataset_type: str = "general") -> List[str]:
    """Generates synthetic data based on the requested type (Fallback)."""
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
    
    technical_topics = [
        "In computer science, a B-tree is a self-balancing tree data structure that maintains sorted data and allows searches, sequential access, insertions, and deletions in logarithmic time.",
        "Gradient descent is a first-order iterative optimization algorithm for finding a local minimum of a differentiable function.",
        "Symmetric-key algorithms are algorithms for cryptography that use the same cryptographic keys for both encryption of plaintext and decryption of ciphertext.",
        "A convolutional neural network (CNN) is a class of deep neural networks, most commonly applied to analyzing visual imagery.",
        "Docker is a set of platform as a service (PaaS) products that use OS-level virtualization to deliver software in packages called containers.",
        "Kubernetes is an open-source container-orchestration system for automating computer application deployment, scaling, and management.",
        "Recursion in computer science is a method of solving a problem where the solution depends on solutions to smaller instances of the same problem."
    ]
    
    legal_topics = [
        "A contract is a legally binding agreement which recognizes and governs the rights and duties of the parties to the agreement.",
        "Tort law is the area of law that covers most civil suits using case law and statutes to provide relief for wrongful acts.",
        "Intellectual property is a category of property that includes intangible creations of the human intellect.",
        "Habeas corpus is a recourse in law through which a person can report an unlawful detention or imprisonment to a court.",
        "Double jeopardy is a procedural defence that prevents an accused person from being tried again on the same (or similar) charges.",
        "Affidavit is a written statement confirmed by oath or affirmation, for use as evidence in court.",
        "Subpoena is a writ ordering a person to attend a court."
    ]

    if dataset_type == "medical": 
        return general_topics + technical_topics
    elif dataset_type == "legal":
        return legal_topics * 2
    elif dataset_type == "technical":
        return technical_topics * 2
    else:
        return general_topics + technical_topics + legal_topics
def load_real_dataset(dataset_type: str = "general", sample_size: int = 50) -> List[str]:
    """
    Loads real-world datasets from HuggingFace.
    """
    texts = []
    
    if load_dataset is None:
        print("Using synthetic fallback (datasets lib missing)...")
        return generate_synthetic_data(dataset_type)

    print(f"Loading real dataset: {dataset_type}...")
    try:
        if dataset_type == "general":
            # WikiText-2
            ds = load_dataset("wikitext", "wikitext-2-raw-v1", split="test", trust_remote_code=True)
            # Filter empty or short lines
            candidates = [x['text'] for x in ds if len(x['text'].strip()) > 100]
            texts = candidates[:sample_size]
            
        elif dataset_type == "medical":
            # PubMed QA
            ds = load_dataset("pubmed_qa", "pqa_labeled", split="train", trust_remote_code=True)
            # Contexts are lists of strings
            candidates = [" ".join(x['context']['contexts']) for x in ds]
            # Filter short
            candidates = [c for c in candidates if len(c) > 100]
            texts = candidates[:sample_size]
            
        elif dataset_type == "legal":
            # BillSum (US Legislation)
            ds = load_dataset("billsum", split="test", trust_remote_code=True)
            candidates = [x['text'] for x in ds if len(x['text']) > 100]
            texts = candidates[:sample_size]
            
        else:
            # Fallback to synthetic
            return generate_synthetic_data("general")
            
    except Exception as e:
        print(f"Error loading dataset {dataset_type}: {e}")
        print("Falling back to synthetic data.")
        return generate_synthetic_data(dataset_type)
        
    if len(texts) < sample_size:
        print(f"Warning: Only found {len(texts)} samples for {dataset_type}.")
        
    # Clean up newlines for consistency
    texts = [t.replace('\n', ' ').strip() for t in texts]
    
    # Truncate to max characters to avoid Tokenizer/CUDA errors (e.g. 512 token limit)
    # 2048 chars is roughly 400-600 tokens
    texts = [t[:2048] for t in texts]
    
    return texts


def prepare_datasets(texts: List[str], split_ratio: float = 0.8) -> Tuple[List[str], List[str]]:
    # Shuffle to ensure randomness
    random.seed(42)
    random.shuffle(texts)
    split_idx = int(len(texts) * split_ratio)
    member_set = texts[:split_idx]
    non_member_set = texts[split_idx:]
    return member_set, non_member_set

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
        """
        Identifies the 'hardest to predict' words and masks them.
        Returns: masked_text, ground_truth_dict
        """
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=1024).to(self.device)
        input_ids = inputs["input_ids"]
        
        with torch.no_grad():
            outputs = self.model(**inputs, labels=input_ids)
            logits = outputs.logits
            
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = input_ids[..., 1:].contiguous()
            
            loss_fct = torch.nn.CrossEntropyLoss(reduction='none')
            loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
            
        # Get top-k indices. adjusting for shift (loss index i corresponds to token i+1)
        top_k_indices = torch.argsort(loss, descending=True)[:num_masks]
        top_k_indices = top_k_indices + 1 
        
        top_k_indices = top_k_indices.cpu().numpy().tolist()
        masked_tokens = list(input_ids[0].cpu().numpy())
        ground_truth = {}
        
        token_strs = [self.tokenizer.decode([t]) for t in masked_tokens]
        
        # Sort indices descending so we can process without affecting earlier indices logic?
        # Actually we operate on list so index is stable until we modify list structure.
        # But here we just replace string in list.
        
        for i, idx in enumerate(top_k_indices):
            if idx < len(token_strs):
                original = token_strs[idx]
                token_strs[idx] = f" [MASK_{i+1}]"
                ground_truth[f"[MASK_{i+1}]"] = original.strip()
            
        masked_text = "".join(token_strs)
        return masked_text, ground_truth

# --- Step 3: RAG System ---
class RAGSystem:
    def __init__(self, config: MIAConfig, member_texts: List[str]):
        self.config = config
        print(f"Initializing RAG with LLM={config.llm_model} and Embed={config.embedding_model}")
        
        self.embeddings = HuggingFaceEmbeddings(model_name=config.embedding_model)
        
        print("Building Vector Store...")
        if config.retriever_type == "bm25":
            if BM25Retriever is None:
                raise ImportError("BM25Retriever not found. Please install rank_bm25: pip install rank_bm25")
            print("Building BM25 Retriever...")
            self.retriever = BM25Retriever.from_texts(member_texts)
            self.retriever.k = config.top_k_retrieval
        elif config.retriever_type == "faiss":
            self.vector_store = FAISS.from_texts(member_texts, self.embeddings)
            self.retriever = self.vector_store.as_retriever(search_kwargs={"k": config.top_k_retrieval})
        else:
            print(f"Warning: Unknown retriever type '{config.retriever_type}'. Defaulting to FAISS.")
            self.vector_store = FAISS.from_texts(member_texts, self.embeddings)
            self.retriever = self.vector_store.as_retriever(search_kwargs={"k": config.top_k_retrieval})

        
        
        # Ensure model is available
        ensure_ollama_model(config.llm_model)
        
        self.llm = OllamaClass(model=config.llm_model, temperature=0, num_predict=50) # Low temp, limit output
        
        template = """You are a helpful assistant. Use the following pieces of context to fill in the missing [MASK_N] placeholders in the text.
        
        Context:
        {context}
        
        Please provide the original words for the placeholders in the format:
        [MASK_1]: answer
        [MASK_2]: answer
        
        Text to fill:
        {question}
        """
        self.qa_prompt = PromptTemplate(template=template, input_variables=["context", "question"])
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={"prompt": self.qa_prompt}
        )

    def query(self, masked_text: str) -> str:
        return self.qa_chain.invoke(masked_text)['result']

# --- Step 4 & 5: Attack & Evaluation ---
class MIAAttacker:
    def __init__(self, config: MIAConfig):
        self.config = config
        self.proxy = ProxyModel(model_name=config.proxy_model)
    
    def evaluate_response(self, response: str, ground_truth: Dict[str, str]) -> float:
        """
        Calculates accuracy of RAG response against ground truth.
        """
        correct_count = 0
        total_masks = len(ground_truth)
        
        if total_masks == 0:
            return 0.0
            
        # Parse response. Expecting "[MASK_N]: answer"
        # We'll normalize text to lowercase and remove punctuation for comparison
        response_lower = response.lower()
        
        for mask_key, answer in ground_truth.items():
            answer_clean = answer.lower().strip()
            # Check if answer is associated with mask key in response
            # Heuristic: Find mask key line, check if answer is in it
            # Or just check if answer appears near mask key
            
            # Simple parsing:
            # Pattern: \[MASK_\d+\]:?\s*(.*)
            # But let's act robustly: search for mask key and see if answer follows
            
            if mask_key.lower() in response_lower:
                # Extract segment after mask key
                part = response_lower.split(mask_key.lower())[1]
                # Take first line or reasonable chunk
                line = part.split('\n')[0]
                if answer_clean in line:
                    correct_count += 1
        
        return correct_count / total_masks

    def run_attack(self, rag_system: RAGSystem, documents: List[str], is_member: bool) -> List[Dict]:
        results = []
        label = 1 if is_member else 0
        
        print(f"Running attack on {'Members' if is_member else 'Non-Members'}...")
        for doc in tqdm(documents):
            # 1. Generate Masks
            masked_text, ground_truth = self.proxy.rank_words(doc, num_masks=self.config.num_masks)
            
            # 2. Query RAG
            try:
                response = rag_system.query(masked_text)
                
                # 3. Score
                accuracy = self.evaluate_response(response, ground_truth)
                
                results.append({
                    "text_preview": doc[:30],
                    "is_member": label,
                    "accuracy": accuracy,
                    "ground_truth": ground_truth,
                    "response_preview": response[:50]
                })
            except Exception as e:
                print(f"  Error querying RAG: {e}")
                results.append({
                    "text_preview": doc[:30],
                    "is_member": label,
                    "accuracy": 0.0,
                    "error": str(e)
                })
                
        return results

def plot_roc_curve(y_true, y_scores, title="ROC Curve"):
    if len(y_true) == 0:
        print("Error: No results to plot (y_true is empty).")
        return 0.0
        
    unique_labels = set(y_true)
    if len(unique_labels) < 2:
        print(f"Warning: Only one class present in results {unique_labels}. Cannot compute ROC AUC.")
        return 0.5

    try:
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
        
        print(f"AUC Score: {roc_auc:.4f}")
        return roc_auc
    except Exception as e:
        print(f"Error plotting ROC curve: {e}")
        return 0.0

def calculate_metrics(y_true, y_scores):
    """
    Calculates detailed metrics including Accuracy, Precision, Recall, F1, 
    and checks for the optimal threshold using Youden's J statistic.
    """
    fpr, tpr, thresholds = roc_curve(y_true, y_scores)
    
    # Avoid division by zero if simple case
    if len(thresholds) == 0:
        return {}

    # Optimal threshold (Maximize TPR - FPR)
    J = tpr - fpr
    ix = np.argmax(J)
    best_thresh = thresholds[ix]
    
    # Binarize predictions based on best threshold
    y_pred = [1 if score >= best_thresh else 0 for score in y_scores]
    
    # Calculate metrics
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    
    metrics = {
        "AUC": auc(fpr, tpr),
        "Best Threshold": best_thresh,
        "Accuracy": acc,
        "Precision": prec,
        "Recall": rec,
        "F1 Score": f1,
        "TP": tp, "TN": tn, "FP": fp, "FN": fn
    }
    
    print("\n--- Detailed Evaluation Metrics (at optimal threshold) ---")
    for k, v in metrics.items():
        if isinstance(v, float):
            print(f"{k}: {v:.4f}")
        else:
            print(f"{k}: {v}")
            
    return metrics

def log_results_to_markdown(config: MIAConfig, metrics: Dict, filename="experiment_results.md"):
    """Appends experiment results to a markdown file."""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    md_content = f"""
## Experiment Run: {timestamp}

### Configuration
- **LLM**: `{config.llm_model}`
- **Embedding**: `{config.embedding_model}`
- **Dataset**: `{config.dataset_type}`
- **Masks per Doc**: {config.num_masks}
- **Retriever**: `{config.retriever_type}`

### Results
| Metric | Value |
|--------|-------|
| **AUC** | **{metrics.get('AUC', 0):.4f}** |
| Accuracy | {metrics.get('Accuracy', 0):.4f} |
| Precision | {metrics.get('Precision', 0):.4f} |
| Recall | {metrics.get('Recall', 0):.4f} |
| F1 Score | {metrics.get('F1 Score', 0):.4f} |
| Best Threshold | {metrics.get('Best Threshold', 0):.4f} |

**Confusion Matrix:**
- True Positives (Member detected as Member): {metrics.get('TP', 0)}
- True Negatives (Non-Member detected as Non-Member): {metrics.get('TN', 0)}
- False Positives (Non-Member detected as Member): {metrics.get('FP', 0)}
- False Negatives (Member detected as Non-Member): {metrics.get('FN', 0)}

---
"""
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(md_content)
        print(f"\nResults successfully appended to {filename}")
    except Exception as e:
        print(f"Failed to log results to markdown: {e}")

# --- Main Execution Loop ---
def run_experiment(config: MIAConfig):
    print(f"\n--- Starting Experiment: {config} ---")
    
    # 1. Prepare Data
    # 1. Prepare Data
    # Increased sample size for better stats with real data
    data = load_real_dataset(config.dataset_type, sample_size=40) 
    members, non_members = prepare_datasets(data)
    
    # 2. Setup RAG
    rag = RAGSystem(config, members)
    
    # 3. Setup Attacker
    attacker = MIAAttacker(config)
    
    # 4. Run Attack
    results_member = attacker.run_attack(rag, members, is_member=True)
    results_non_member = attacker.run_attack(rag, non_members, is_member=False)
    
    # 5. Evaluate
    all_results = results_member + results_non_member
    y_true = [r['is_member'] for r in all_results]
    y_scores = [r['accuracy'] for r in all_results]
    
    # Plot ROC
    # plot_roc_curve(y_true, y_scores, title=f"ROC - {config.llm_model} - {config.dataset_type}")
    
    # Calculate Detailed Metrics
    metrics = calculate_metrics(y_true, y_scores)
    
    # Log to Markdown
    log_results_to_markdown(config, metrics)
    
    return all_results, metrics

if __name__ == "__main__":
    # Framework for Ablation Studies & Variations
    print("--- Starting Ablation Studies ---")
    
    # Configuration Matrix
    llm_options = ["llama3", "mistral", "phi3"]
    embedding_options = ["sentence-transformers/all-MiniLM-L6-v2", "BAAI/bge-small-en-v1.5"]
    retriever_options = ["faiss", "bm25"]
    dataset_options = ["general", "medical", "legal"]
    
    # Iterate through all combinations
    total_runs = len(llm_options) * len(embedding_options) * len(retriever_options) * len(dataset_options)
    current_run = 0
    
    for llm in llm_options:
        for embed in embedding_options:
            for ret in retriever_options:
                for data_type in dataset_options:
                    current_run += 1
                    print(f"\n[{current_run}/{total_runs}] Running Configuration: LLM={llm}, Embed={embed}, Ret={ret}, Data={data_type}")
                    
                    config = MIAConfig(
                        llm_model=llm,
                        embedding_model=embed,
                        retriever_type=ret,
                        dataset_type=data_type,
                        num_masks=5,  # Fixed as per rigorous eval
                        top_k_retrieval=3
                    )
                    
                    try:
                        results, metrics = run_experiment(config)
                        # Optional: Clear CUDA cache if using GPU to prevent OOM
                        if torch.cuda.is_available():
                            torch.cuda.empty_cache()
                            
                    except Exception as e:
                        print(f"!!! Run Failed for {config}: {e}")
                        # Log failure explicitly
                        try:
                            with open("experiment_failures.log", "a") as f:
                                f.write(f"Failed Config: {config}\nError: {e}\n\n")
                        except:
                            pass
                            
    print("\n--- Ablation Studies Framework Completed ---")


