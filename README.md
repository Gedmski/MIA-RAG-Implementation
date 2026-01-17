# MIA-RAG-Implementation

This project implements a **Membership Inference Attack (MIA)** pipeline against **Retrieval-Augmented Generation (RAG)** systems. based on the research paper "Mask-based Membership Inference Attacks for Retrieval-Augmented Generation" (Liu et al., 2025). It evaluates whether a specific text document was part of the RAG system's knowledge base (member) or not (non-member).

## Project Goal
Build a local RAG system and attack it using a "Mask-Based" approach. The attack works by masking "hard-to-predict" words in a document and asking the RAG system to fill them in.
- **Hypothesis**: If the document is in the RAG's database, it will retrieve the exact text and fill the masks perfectly. If not, it will struggle.

## Key Results
Based on our ablation studies, the attack is highly effective under specific configurations:

- **Best Configuration**: `llama3` + `sentence-transformers/all-MiniLM-L6-v2` + `faiss` achieved **AUC: 1.0000**.
- **LLM Performance**: `llama3` consistently outperformed `mistral` and `phi3`, with an average AUC of **0.99**.
- **Dataset**: The attack was most effective on the **Medical** dataset (AUC 0.95), suggesting domain-specific data is more vulnerable than general text.

Running `process_results.py` will generate a detailed [Results Report](results_report.md) and a raw CSV of all experiments.

## Project Structure

- `mia_rag_attack.py`: The main script that runs the ablation studies and attacks.
- `process_results.py`: Script to parse results and generate reports.
- `experiment_results.md`: Raw log of experiment results.
- `results_report.md`: detailed analysis of the experiments.
- `experiment_data.csv`: Structured CSV data of all runs.

## Prerequisites

### 1. Python Environment
Ensure you have Python 3.8+ installed. You will need the following libraries:

```bash
pip install torch transformers pandas numpy matplotlib scikit-learn langchain langchain-community langchain-huggingface rank_bm25 datasets tqdm requests
```

### 2. Ollama
This project uses [Ollama](https://ollama.com/) to run local LLMs (Llama 3, Mistral, Phi-3).

1.  **Install Ollama**: Follow instructions at [ollama.com](https://ollama.com/).
2.  **Pull Required Models**:
    ```bash
    ollama pull llama3
    ollama pull mistral
    ollama pull phi3
    ```
3.  **Start Ollama**: Ensure the Ollama service is running (`ollama serve`).

## Usage

To run the full suite of ablation studies (testing various LLMs, embeddings, retrievers, and datasets):

```bash
python mia_rag_attack.py
```

### Configuration Matrix
The script automatically iterates through the following combinations:
-   **LLMs**: `llama3`, `mistral`, `phi3`
-   **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`, `BAAI/bge-small-en-v1.5`
-   **Retrievers**: `FAISS` (Dense), `BM25` (Sparse)
-   **Datasets**: `general` (WikiText), `medical` (PubMedQA), `legal` (BillSum)
