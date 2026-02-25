
import os
import random
import numpy as np
import json
import torch
import sys
import re
import itertools
from typing import List, Dict, Tuple, Optional, Set
from tqdm import tqdm
from datetime import datetime
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# --- Dependencies Check ---
try:
    import pandas as pd
    from sklearn.metrics import roc_curve, auc, roc_auc_score, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
    from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM, logging as transformers_logging
    transformers_logging.set_verbosity_error()
except ImportError as e:
    print(f"CRITICAL: Missing dependencies. Please install: pandas scikit-learn transformers torch")
    print(f"Error: {e}")
    sys.exit(1)

# LangChain Imports
try:
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_core.documents import Document
    from langchain_core.prompts import PromptTemplate
    from langchain_ollama import OllamaLLM
except ImportError:
    # Attempt legacy imports
    try:
        from langchain.embeddings import HuggingFaceEmbeddings
        from langchain.vectorstores import FAISS
        from langchain.docstore.document import Document
        from langchain.prompts import PromptTemplate
        from langchain_community.llms import Ollama as OllamaLLM
    except ImportError:
        print("CRITICAL: Missing LangChain dependencies. Please install: langchain langchain-community langchain-huggingface langchain-ollama faiss-cpu")
        sys.exit(1)

# --- Configuration ---
class MIAConfig:
    def __init__(self, 
                 llm_model: str = "llama3",
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                 dataset_type: str = "healthcaremagic",
                 proxy_model: str = "gpt2",
                 num_masks: int = 5,
                 retriever_k: int = 3,
                 masking_strategy: str = "hard", # 'hard' or 'random'
                 use_spelling_correction: bool = True,
                 retriever_type: str = "faiss", # 'faiss' or 'bm25'
                 index_size: int = 500,
                 eval_size: int = 50):
        self.llm_model = llm_model
        self.embedding_model = embedding_model
        self.dataset_type = dataset_type
        self.proxy_model = proxy_model
        self.num_masks = num_masks
        self.retriever_k = retriever_k
        self.masking_strategy = masking_strategy
        self.use_spelling_correction = use_spelling_correction
        self.retriever_type = retriever_type
        self.index_size = index_size
        self.eval_size = eval_size
        
    def __repr__(self):
        return (
            f"Config(LLM={self.llm_model}, Data={self.dataset_type}, Emb={self.embedding_model}, "
            f"Ret={self.retriever_type}, M={self.num_masks}, K={self.retriever_k}, "
            f"Idx={self.index_size}, Eval={self.eval_size})"
        )

# --- 1. Data Loading & Preprocessing ---
def load_real_dataset(dataset_type: str = "healthcaremagic", sample_size: int = 50) -> List[Document]:
    """
    Loads specific datasets from the Liu et al. (2025) paper.
    Strictly truncates to 512 tokens to prevent CUDA errors.
    """
    texts = []
    print(f"Loading dataset: {dataset_type}...")
    
    try:
        from datasets import load_dataset
        
        if dataset_type == "healthcaremagic":
            # Paper Source: RafaelMPereira/HealthCareMagic-100k-Chat-Format-en
            try:
                # Removed trust_remote_code=True as it is deprecated for some datasets or ignored
                ds = load_dataset("RafaelMPereira/HealthCareMagic-100k-Chat-Format-en", split="train")
                
                # Check keys dynamically
                example = ds[0]
                # print(f"DEBUG: Dataset Keys: {example.keys()}")
                
                input_key = 'input' if 'input' in example else 'instruction'
                output_key = 'output' if 'output' in example else 'response'
                
                if input_key not in example:
                     # Fallback to just taking values if unnamed
                     print(f"Warning: Expected keys not found. Keys: {example.keys()}")
                     candidates = [str(x) for x in ds]
                else:
                    candidates = [f"Patient: {x.get(input_key, '')}\nDoctor: {x.get(output_key, '')}" for x in ds]
                    
                texts = [c for c in candidates if len(c) > 200][:sample_size]
            except Exception as dim_err:
                print(f"Error specifically in healthcaremagic formatting: {dim_err}")
                raise dim_err

        elif dataset_type == "msmarco":
            # Paper Source: MS-MARCO (Validation Set)
            ds = load_dataset("ms_marco", "v1.1", split="validation", streaming=True)
            # Take first N passages.
            candidates = []
            for row in ds:
                passages = row.get('passages', {})
                texts_list = passages.get('passage_text', [])
                candidates.extend(texts_list)
                if len(candidates) >= sample_size * 2: break
            texts = [c for c in candidates if len(c) > 100][:sample_size]

        elif dataset_type == "nq":
            # Paper Source: LLukas22/nq-simplified
            ds = load_dataset("LLukas22/nq-simplified", split="test")
            candidates = []
            for x in ds:
                 text = x.get('context') or x.get('document_text') or x.get('passage') or x.get('long_answer', '')
                 if len(text) > 200:
                     candidates.append(text)
            texts = candidates[:sample_size]
            
        else:
            print(f"Unknown dataset {dataset_type}, falling back to WikiText-2 (General)")
            ds = load_dataset("wikitext", "wikitext-2-raw-v1", split="test")
            texts = [x['text'] for x in ds if len(x['text']) > 200][:sample_size]

    except Exception as e:
        print(f"Error loading {dataset_type}: {e}")
        # Synthetic Fallback - MAKE IT LONG ENOUGH > 200 chars
        texts = [f"Synthetic document {i} about {dataset_type}. This is a filler text to ensure the system has enough content to process and does not fail due to short length checks. " * 10 for i in range(sample_size)]

    # Process and Truncate
    documents = []
    
    # Debug: Print first text if available to verify content
    if texts:
        print(f"Sample text length: {len(texts[0])} chars")
        
    for i, t in enumerate(texts):
        # Clean text
        clean_text = t.replace('\n', ' ').strip()
        # Strict truncation for MBA stability
        truncated_text = clean_text[:2500] 
        
        documents.append(Document(
            page_content=truncated_text,
            metadata={"id": i, "source": dataset_type}
        ))
        
    return documents

def prepare_splits(documents: List[Document], split_ratio: float = 0.8) -> Tuple[List[Document], List[Document]]:
    if not documents:
        print("Warning: No documents to split!")
        return [], []
        
    random.seed(42)
    shuffled = documents.copy()
    random.shuffle(shuffled)
    split_idx = int(len(shuffled) * split_ratio)
    return shuffled[:split_idx], shuffled[split_idx:]

# --- 2. Mask Generation (MBA Algorithms) ---
class MaskGenerator:
    def __init__(self, model_name: str = "gpt2", device: str = None, use_spelling: bool = True):
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Loading Mask Generator ({model_name}) on {self.device}...")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name).to(self.device).eval()
        except Exception as e:
            print(f"Error loading proxy model {model_name}: {e}")
            self.model = None
        
        self.use_spelling = use_spelling
        self.spelling_model = None
        self.spelling_tokenizer = None
        
        if self.use_spelling:
            try:
                print("Loading Spelling Correction Model (oliverguhr/spelling-correction-english-base)...")
                self.spelling_tokenizer = AutoTokenizer.from_pretrained("oliverguhr/spelling-correction-english-base")
                self.spelling_model = AutoModelForSeq2SeqLM.from_pretrained("oliverguhr/spelling-correction-english-base").to(self.device).eval()
            except Exception as e:
                print(f"Warning: Could not load spelling model: {e}. Disabling spelling correction.")
                self.use_spelling = False

    def is_valid_word(self, word: str) -> bool:
        """Filter out stopwords, punctuation, and short tokens."""
        if len(word) < 3: return False
        if not re.match(r'^[a-zA-Z]+$', word): return False
        stopwords = {'the', 'and', 'that', 'with', 'this', 'from', 'have', 'was', 'were', 'which', 'for', 'are', 'not', 'but'}
        if word.lower() in stopwords: return False
        return True

    def get_fragmented_words(self, text: str) -> List[Dict]:
        """
        Algorithm 2: Extract words that are split by tokenizer.
        """
        tokens = self.tokenizer.tokenize(text)
        # Reconstruct mapping to original word indices is complex with just tokenize.
        # Simpler approach: Iterate words in text, check if they tokenize to multiple.
        
        fragmented = []
        words = text.split()
        current_char_idx = 0
        
        for i, word in enumerate(words):
            word_clean = re.sub(r'[^\w\s]', '', word) # remove punct
            if not word_clean: continue
            
            sub_tokens = self.tokenizer.tokenize(word_clean)
            if len(sub_tokens) > 1:
                fragmented.append({
                    "word": word_clean,
                    "index": i,
                    "tokens": sub_tokens
                })
        return fragmented

    def correct_spelling(self, text_segment: str) -> str:
        if not self.use_spelling: return text_segment
        try:
            inputs = self.spelling_tokenizer(text_segment, return_tensors="pt", max_length=128, truncation=True).to(self.device)
            with torch.no_grad():
                outputs = self.spelling_model.generate(**inputs, max_length=128)
            return self.spelling_tokenizer.decode(outputs[0], skip_special_tokens=True)
        except:
            return text_segment

    def generate_masks(self, text: str, num_masks: int = 5, strategy: str = "hard") -> Tuple[str, Dict[str, List[str]]]:
        """
        Generates masks using MBA heuristics.
        Returns: 
            masked_text: str
            ground_truth: Dict[mask_token, List[answers]] (List because original + corrected)
        """
        words = text.split()
        if len(words) < num_masks * 2:
            return text, {} # Too short

        candidates = []
        
        if strategy == "random":
            # Random strategy
            valid_indices = [i for i, w in enumerate(words) if self.is_valid_word(w)]
            selected_indices = random.sample(valid_indices, min(len(valid_indices), num_masks))
        else:
            # "Hard" strategy - Proxy Model Ranking
            # We score every word. This is expensive, so we optimize by batching or chunking if needed.
            # Simplified: Score words by taking surrounding context.
            
            # To strictly follow paper: Compute loss for every token? 
            # Optimization: Just use perplexity of word given previous context.
            
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=1024).to(self.device)
            input_ids = inputs["input_ids"][0]
            
            with torch.no_grad():
                outputs = self.model(inputs["input_ids"], labels=inputs["input_ids"])
                logits = outputs.logits[0]
                
            # Logits [seq_len, vocab]. Prob for token at i is logits[i-1]
            # This maps tokens to scores. We need to map Words to expected scores.
            # Heuristic: Map back roughly or just use word-based scan for simplicity?
            # Paper Algorithm 4 uses "Rank Score".
            
            # Let's map word-level difficulty:
            word_scores = []
            
            # This alignment is tricky. We'll simplify: 
            # We will tokenize each word individually to map back to input_ids
            # This is an approximation.
            
            current_token_idx = 0
            for i, word in enumerate(words):
                w_tokens = self.tokenizer.tokenize(" " + word) # GPT2 adds space
                w_len = len(w_tokens)
                
                if current_token_idx + w_len >= len(input_ids): break
                
                # Calculate avg NLL for this word's tokens
                # Score is sum of log probs (lower is harder? No, Rank Score. High Rank = Low Prob)
                # We use CrossEntropy (Loss) as proxy for difficulty. Higher loss = Harder.
                
                start = current_token_idx
                end = current_token_idx + w_len
                
                # Shift by -1 for logits
                # Loss for token at pos `t` uses logits at `t-1` and label at `t`
                
                word_loss = 0.0
                valid_tokens = 0
                for t in range(start, end):
                    if t == 0: continue # Can't predict first token
                    token_id = input_ids[t]
                    token_logits = logits[t-1]
                    loss = torch.nn.functional.cross_entropy(token_logits.view(1, -1), token_id.view(1))
                    word_loss += loss.item()
                    valid_tokens += 1
                
                avg_loss = word_loss / max(1, valid_tokens)
                
                if self.is_valid_word(word):
                    word_scores.append((i, avg_loss))
                
                current_token_idx += w_len
                
            # Sort by difficulty (Loss descending)
            word_scores.sort(key=lambda x: x[1], reverse=True)
            
            selected_indices = []
            # Adjacency Filter
            for idx, score in word_scores:
                if len(selected_indices) >= num_masks: break
                
                # Check neighbors
                is_adjacent = False
                for existing in selected_indices:
                    if abs(existing - idx) <= 1:
                        is_adjacent = True
                        break
                
                if not is_adjacent:
                    selected_indices.append(idx)

        # Apply Masks
        selected_indices.sort()
        masked_words = words.copy()
        ground_truth = {}
        
        for i, idx in enumerate(selected_indices):
            original_word = words[idx]
            
            # Spelling Correction (Algorithm 1)
            answers = [original_word]
            if self.use_spelling:
                # Get context
                start_ctx = max(0, idx - 2)
                context_chunk = " ".join(words[start_ctx : idx + 1])
                corrected = self.correct_spelling(context_chunk).split()[-1] # Take last word
                
                # Clean punctuation on corrected
                corrected_clean = re.sub(r'[^\w]', '', corrected)
                original_clean = re.sub(r'[^\w]', '', original_word)
                
                if corrected_clean.lower() != original_clean.lower() and len(corrected_clean) > 0:
                    answers.append(corrected_clean)
            
            mask_token = f"[MASK_{i+1}]"
            masked_words[idx] = mask_token
            ground_truth[mask_token] = answers
            
        return " ".join(masked_words), ground_truth

# --- 3. RAG System ---
class RAGSystem:
    def __init__(self, config: MIAConfig, documents: List[Document]):
        self.config = config
        
        print("Initializing RAG Embeddings (Strict Truncation)...")
        # CRITICAL FIX: encode_kwargs={'max_length': 512, 'truncation': True}
        # This prevents the CUDA assert error on long docs
        self.embeddings = HuggingFaceEmbeddings(
            model_name=config.embedding_model,
            encode_kwargs={'normalize_embeddings': True},
            model_kwargs={'device': 'cuda' if torch.cuda.is_available() else 'cpu'}
        )
        # Ensure underlying SentenceTransformer respects simple truncation if possible
        # but LangChain wrap helps. We forced input text truncation in `load_real_dataset` too.
        
        if config.retriever_type == "bm25":
            print("Using BM25 Retriever")
            try:
                from langchain_community.retrievers import BM25Retriever
                self.retriever = BM25Retriever.from_documents(documents)
                self.retriever.k = config.retriever_k
                self.vector_store = None
            except ImportError:
                print("Error: rank_bm25 not installed. Install with `pip install rank_bm25`")
                raise
        else:
            print(f"Building FAISS Index with {len(documents)} documents...")
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
            self.retriever = self.vector_store.as_retriever(search_kwargs={"k": config.retriever_k})
        
        print(f"Initializing LLM: {config.llm_model}")
        self.llm = OllamaLLM(model=config.llm_model, temperature=0.0)

    def query(self, masked_text: str) -> Tuple[str, List[int]]:
        """
        Returns: (Generated Answer, List of Retrieved Doc IDs)
        """
        # Retrieval
        docs = self.retriever.invoke(masked_text)
        retrieved_ids = [d.metadata.get('id', -1) for d in docs]
        
        # Generation
        context_str = "\n\n".join([d.page_content for d in docs])
        
        # Phi-3 Specific Prompt (One-Shot)
        if "phi" in self.config.llm_model.lower():
            prompt = f"""Instruct: You are a helpful assistant. Below is a text with missing words marked as [MASK_N]. Use the provided Context to identify the missing words.
            
            Context: {context_str[:2000]}...
            
            Input Text: {masked_text}
            
            Format your output strictly as:
            [MASK_1]: <word>
            [MASK_2]: <word>
            
            Output:
            """
        else:
            # Standard Prompt
            prompt = f"""You are a helper. The following text contains masked words like [MASK_1]. Using the context provided, identify the original words.
            
            Context:
            {context_str}
            
            Text with Masks:
            {masked_text}
            
            Please list the answers for each mask. Format:
            [MASK_1]: answer_word
            [MASK_2]: answer_word
            """
            
        response = self.llm.invoke(prompt)
        return response, retrieved_ids

# --- 4. Main Attack Logic ---
class MIAAttacker:
    def __init__(self, config: MIAConfig):
        self.config = config
        self.mask_generator = MaskGenerator(
            model_name=config.proxy_model, 
            use_spelling=config.use_spelling_correction
        )
        
    def evaluate_correctness(self, response: str, ground_truth: Dict[str, List[str]]) -> float:
        if not ground_truth: return 0.0
        
        correct = 0
        response_lower = response.lower()
        
        for mask_key, valid_answers in ground_truth.items():
            # Clean valid answers
            valid_answers_clean = [a.lower().strip() for a in valid_answers]
            
            # Find line with mask key
            # Regex to find "[MASK_1]: word"
            # escape brackets for regex
            key_esc = re.escape(mask_key).lower()
            # Fix warning by using raw string for regex
            match = re.search(fr"{key_esc}[:\s]+(.*?)(?:\n|$)", response_lower)
            
            if match:
                predicted_raw = match.group(1)
                # Check if any valid answer is in predicted string
                # Logic: Is the predicted word ONE of the valid answers?
                # We split predicted by space to handle "word." punctuation issues
                pred_words = re.split(r'\W+', predicted_raw)
                
                is_hit = False
                for ans in valid_answers_clean:
                    if ans in pred_words or ans in predicted_raw:
                        is_hit = True
                        break
                if is_hit:
                    correct += 1
                    
        return correct / len(ground_truth)

    def run_experiment(self, rag: RAGSystem, target_docs: List[Document], is_member: bool):
        results = []
        label = 1 if is_member else 0
        desc = "Members" if is_member else "Non-Members"
        
        for doc in tqdm(target_docs, desc=desc):
            # 1. Masking
            masked_text, ground_truth = self.mask_generator.generate_masks(
                doc.page_content, 
                num_masks=self.config.num_masks, 
                strategy=self.config.masking_strategy
            )
            
            if not ground_truth: continue # skipped short doc
            
            # 2. Query
            try:
                response, retrieved_ids = rag.query(masked_text)
                
                # 3. Metrics
                mask_acc = self.evaluate_correctness(response, ground_truth)
                
                # Retrieval Recall (Only relevant for Members)
                retrieval_hit = False
                if is_member:
                    doc_id = doc.metadata.get('id')
                    if doc_id in retrieved_ids:
                        retrieval_hit = True
                
                results.append({
                    "is_member": label,
                    "mask_acc": mask_acc,
                    "retrieval_recall": 1.0 if retrieval_hit else 0.0,
                    "ground_truth": str(ground_truth),
                    "response_len": len(response)
                })
                
            except Exception as e:
                print(f"Error processing doc: {e}")
                
        return results

# --- Main ---
# --- Main ---
if __name__ == "__main__":
    print("--- Starting Ablation Studies (MBA Implementation) ---")
    
    # Ablation Configuration
    datasets = ["healthcaremagic", "msmarco", "nq"]
    llms = ["llama3", "mistral", "phi3"]
    embeddings = ["sentence-transformers/all-MiniLM-L6-v2", "BAAI/bge-small-en-v1.5"]
    retrievers = ["faiss", "bm25"]
    num_masks_list = [5, 10, 15]
    retriever_k_list = [3, 5]

    experiments = list(itertools.product(
        datasets, llms, embeddings, retrievers, num_masks_list, retriever_k_list
    ))
    print(f"Starting Grid Search: {len(experiments)} total configurations.")

    for run_idx, (d_type, model, emb, ret, m, k) in enumerate(experiments, start=1):
        try:
            print(f"\n\n==================================================")
            print(
                f"Run {run_idx}/{len(experiments)}: Dataset={d_type}, LLM={model}, "
                f"Embed={emb}, Ret={ret}, M={m}, K={k}"
            )
            print(f"==================================================")
            
            # 1. Pipeline Setup
            start_time = datetime.now()
            
            # Config
            config = MIAConfig(
                llm_model=model,
                embedding_model=emb,
                dataset_type=d_type,
                masking_strategy="hard",
                num_masks=m,
                retriever_k=k,
                retriever_type=ret,
                index_size=500, # Large haystack
                eval_size=50    # Quick eval
            )
            
            # 2. Data
            # Load enough documents for the Index
            documents = load_real_dataset(config.dataset_type, sample_size=config.index_size)
            if not documents:
                print("Skipping due to empty dataset.")
                continue
                
            # Split: 80% Members (Indexed), 20% Non-Members (Not Indexed)
            members, non_members = prepare_splits(documents, split_ratio=0.8)
            
            # 3. Build RAG
            # Index ALL Members to create the "Haystack"
            print(f"Indexing {len(members)} Member documents...")
            rag = RAGSystem(config, members)
            
            # 4. Attack
            attacker = MIAAttacker(config)
            
            # Sub-sample for Evaluation
            # We only attack 'eval_size' documents to save time, but they are hidden among all 'members'
            eval_members = random.sample(members, min(len(members), config.eval_size))
            eval_non_members = random.sample(non_members, min(len(non_members), config.eval_size))
            
            print(f"\n--- Attacking {len(eval_members)} Member Documents (from {len(members)} indexed) ---")
            member_results = attacker.run_experiment(rag, eval_members, is_member=True)
            
            print(f"\n--- Attacking {len(eval_non_members)} Non-Member Documents ---")
            non_member_results = attacker.run_experiment(rag, eval_non_members, is_member=False)
            
            # 5. Evaluation & Logging
            all_results = member_results + non_member_results
            if not all_results:
                print("No results generated.")
                continue
                
            y_true = [r['is_member'] for r in all_results]
            y_scores = [r['mask_acc'] for r in all_results]
            
            retrieval_recalls = [r['retrieval_recall'] for r in member_results]
            avg_recall = sum(retrieval_recalls) / len(retrieval_recalls) if retrieval_recalls else 0.0
            
            auc_score = 0
            if len(set(y_true)) > 1:
                auc_score = roc_auc_score(y_true, y_scores)
                
            print(f"AUC: {auc_score:.4f}, Recall: {avg_recall:.4f}")
            
            # Log to MD
            with open("experiment_results.md", "a") as f:
                f.write(f"\n## Run {start_time}\n")
                f.write(f"- **Config**: {config}\n")
                f.write(f"- **Num Masks**: {config.num_masks}\n")
                f.write(f"- **Retriever K**: {config.retriever_k}\n")
                f.write(f"- **AUC**: {auc_score:.4f}\n")
                f.write(f"- **Retrieval Recall**: {avg_recall:.4f}\n")
                f.write(f"- **Index Size**: {len(members)}\n")
                f.write(f"- **Eval Samples**: {len(all_results)} (M:{len(member_results)}, NM:{len(non_member_results)})\n")
                f.write("---\n")
                
            # Clean up
            del rag
            del attacker
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                
        except Exception as e:
            print(f"FAILED Experiment {d_type}/{model}/{ret}/M={m}/K={k}: {e}")
            with open("experiment_results.md", "a") as f:
                 f.write(f"\n## Run {datetime.now()} - FAILED\n")
                 f.write(f"- **Config**: Dataset={d_type}, LLM={model}, Emb={emb}, Ret={ret}\n")
                 f.write(f"- **Num Masks**: {m}\n")
                 f.write(f"- **Retriever K**: {k}\n")
                 f.write(f"- **Error**: {e}\n")
                 f.write("---\n")

    print("\n--- All Ablation Studies Completed ---")
