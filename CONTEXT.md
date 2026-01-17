# Project Specification: Mask-Based Membership Inference Attack (MBA) on RAG

## 1. Project Overview
**Goal**: Build a local Retrieval-Augmented Generation (RAG) system and implement a **Mask-Based Membership Inference Attack (MBA)** based on the research paper "Mask-based Membership Inference Attacks for Retrieval-Augmented Generation" (Liu et al., 2025).

**Constraints & Hardware**:
- **Hardware**: NVIDIA RTX 4060 (8GB VRAM).
- **Restrictions**: NO external API keys (OpenAI/Anthropic). All models must run locally.
- **Output**: A single Jupyter Notebook (`MIA_RAG_Attack.ipynb`) containing the full pipeline.

## 2. Technical Stack
The agent must use the following libraries:
- **LLM Serving**: `Ollama` (running `llama3` or `mistral` via `langchain-ollama`).
- **Embeddings**: `HuggingFaceEmbeddings` (model: `BAAI/bge-small-en-v1.5` or `sentence-transformers/all-MiniLM-L6-v2`).
- **Vector DB**: `FAISS` (local, in-memory) or `Chroma`.
- **Proxy Model**: `transformers` library (using `gpt2` or `distilgpt2`) for mask generation ranking.
- **Evaluation**: `scikit-learn` for ROC/AUC metrics.

---

## 3. Implementation Steps

### Step 1: Environment Setup & Data Preparation
*Objective: Prepare a dataset of "Member" (seen) and "Non-Member" (unseen) documents.*

1.  **Synthetic Dataset**: Create a simple function to generate or load a small dataset (e.g., 20 short text passages about specific topics like "Quantum Computing History", "Photosynthesis", etc.).
2.  **Split**: Randomly split this into:
    - `Member_Set` (80%): These will be indexed in the RAG.
    - `Non_Member_Set` (20%): These will NOT be in the RAG but used to test the attack.

### Step 2: RAG Implementation (The Target)
*Objective: Build the "Black Box" RAG system we want to attack.*

1.  **Vector Store**: Ingest `Member_Set` into a FAISS index using the chosen HuggingFace embedding model.
2.  **Retriever**: Configure a standard retriever (k=3).
3.  **Generation Chain**: Set up a LangChain pipeline using Ollama.
    - **Prompt Template**: Standard RAG prompt ("Answer based on context...").
    - **Model**: Use `ollama.chat` with `temperature=0` for deterministic results.

### Step 3: Mask Generation (The Attack Component)
*Objective: Implement the "Proxy Language Model" masking logic from the paper.*

The paper defines **MBA** as masking words that are "hard to predict" without context.
1.  **Load Proxy Model**: Load `gpt2` (small, fast) using HuggingFace `AutoModelForCausalLM`.
2.  **Rank Function**: Create a function `rank_words(text, num_masks=5)`:
    - Tokenize the text.
    - For every word, calculate its probability/rank given the preceding context using `gpt2`.
    - **Logic**: A high "rank score" means the word is hard to predict (low probability).
    - Select the top $M$ words with the highest difficulty.
3.  **Masking**: Replace these words with a placeholder (e.g., `[MASK_1]`, `[MASK_2]`).
    - *Note*: Ensure you store the "Ground Truth" answers for these masks.

### Step 4: Attack Execution
*Objective: Probe the RAG system to see if it recognizes the member data.*

1.  **Prompting**: Feed the *masked* text into the RAG system.
    - **Attack Prompt**: "Please fill in the missing [MASK_i] placeholders in the following text. Output format: [MASK_1]: answer."
2.  **Hypothesis**:
    - If the document **IS** in the DB, the RAG will retrieve the original text and fill the masks perfectly.
    - If the document **IS NOT** in the DB, the RAG will struggle to guess the "hard-to-predict" words.

### Step 5: Scoring & Evaluation
*Objective: Calculate metrics.*

1.  **Accuracy Metric**: For each document, calculate `Mask_Accuracy` = (Correctly Filled Masks / Total Masks).
2.  **Comparison**:
    - Run the attack on `Member_Set` (expect High Accuracy).
    - Run the attack on `Non_Member_Set` (expect Low Accuracy).
3.  **ROC/AUC**:
    - Use `y_true` (1 for Member, 0 for Non-Member).
    - Use `y_score` (The Mask_Accuracy for that document).
    - Plot the ROC Curve.

---

## 4. Code Reference (Python Snippets)

**A. Proxy Model Ranking (Critical Paper Logic)**
```python
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")

def get_hardest_words(text, top_k=3):
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs, labels=inputs["input_ids"])
        # Calculate loss/logits per token to estimate "surprise"
        # High loss = Hard to predict = Good candidate for masking
        shift_logits = outputs.logits[..., :-1, :].contiguous()
        shift_labels = inputs["input_ids"][..., 1:].contiguous()
        loss_fct = torch.nn.CrossEntropyLoss(reduction='none')
        loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
        
    # Get indices of tokens with highest loss
    top_indices = torch.argsort(loss, descending=True)[:top_k]
    return top_indices

```

**B. RAG Setup with Ollama**

```python
from langchain_community.llms import Ollama
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

llm = Ollama(model="llama3") # Or mistral
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_db = FAISS.from_texts(member_texts, embeddings)
retriever = vector_db.as_retriever()

```

## 5. Deliverables

1. **Jupyter Notebook**: Fully commented.
2. **Visualization**: A Matplotlib graph showing the separation between Member and Non-Member accuracy scores.
3. **Baseline Comparison**: (Optional) Compare against a "Random Masking" baseline where we mask random words instead of "hard" words.

**Action**: Please generate the code to implement this specification.