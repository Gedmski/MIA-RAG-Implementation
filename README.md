# Mask-Based Membership Inference Attack (MBA) Implementation

This repository contains the implementation of the **Mask-Based Membership Inference Attack (MBA)** framework for Retrieval-Augmented Generation (RAG) systems, as described in *Liu et al. (2025)*.

> **Latest Update (Jan 2026)**: The codebase has been overhauled to strictly adhere to the paper's methodology, including Fragmented Word Extraction, Spelling Correction, and Adjacency Filtering. It now supports extensive ablation studies across multiple LLMs and Retrievers.

## Project Structure

- `mia_rag_attack.py`: The main script implementing the MBA attack and Ablation Study runner.
- `mia_rag_attack.py` (Core Logic):
    - **Masking**: Hard/Random strategies, Spelling Correction, Fragmented Word handling.
    - **RAG**: FAISS & BM25 retrievers, dynamic index/eval sizing.
- `process_results.py`: Analyzes `experiment_results.md` and generates summary reports.
- `experiment_results.md`: Raw log of experiment runs.
- `results_report.md`: Aggregated summary of findings.
- `LOGS.md`: Detailed project change log.

## Prerequisites

1.  **Python 3.10+**
2.  **Ollama**: Required to serve the LLM (e.g., Llama 3, Phi-3, Mistral).
    - [Download Ollama](https://ollama.com/)
    - Pull the models you intend to use:
      ```bash
      ollama pull llama3
      ollama pull mistral
      ollama pull phi3
      ```

## Installation

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: A GPU is highly recommended for the Embedding and Proxy (GPT-2) models.*

2.  **Verify Ollama**:
    Ensure Ollama is running in the background (`ollama serve`).

## Usage

### Running Ablation Studies (Default)
The script is currently configured to run a **Full Grid Search** (Ablation Study) across all supported configurations to reproduce the paper's findings.

```bash
python mia_rag_attack.py
```

**This will run 36+ experiments** iterating through:
- **Datasets**: `healthcaremagic`, `msmarco`, `nq`
- **LLMs**: `llama3`, `mistral`, `phi3`
- **Embeddings**: `all-MiniLM-L6-v2`, `bge-small-en-v1.5`
- **Retrievers**: `faiss` (Dense), `bm25` (Sparse)

### Running a Single Experiment
To run a specific configuration, you must modify the `__main__` block at the bottom of `mia_rag_attack.py`.

Example configuration for a single run:

```python
if __name__ == "__main__":
    config = MIAConfig(
        llm_model="llama3",
        dataset_type="healthcaremagic",
        masking_strategy="hard",
        retriever_type="faiss",
        index_size=500,  # Size of the RAG Knowledge Base
        eval_size=50     # Number of documents to attack (subset of index)
    )
    # ... call pipeline setup ...
```

## Configuration

The `MIAConfig` class controls the attack parameters:

| Parameter | Options / Description | Default |
| :--- | :--- | :--- |
| `dataset_type` | `healthcaremagic`, `msmarco`, `nq` | `healthcaremagic` |
| `llm_model` | `llama3`, `mistral`, `phi3` (Ollama models) | `llama3` |
| `retriever_type` | `faiss` (Vector), `bm25` (Keyword) | `faiss` |
| `embedding_model` | HF Model ID for FAISS (e.g., `all-MiniLM-L6-v2`) | `all-MiniLM-L6-v2` |
| `masking_strategy` | `hard` (GPT-2 Perplexity), `random` | `hard` |
| `num_masks` | Number of words to mask per document | `5` |
| `index_size` | Number of documents in the RAG "Haystack" | `500` |
| `eval_size` | Number of specific documents to target for MIA | `50` |

### Key Methodology Updates
1.  **Index vs. Eval Decoupling**: To simulate realistic retrieval challenges without excessive compute, we index a larger set (`index_size=500`) but only attack a smaller subset (`eval_size=50`).
2.  **Fragmented Word Extraction**: Ensures that words split by tokens (e.g., "baker" -> "bak", "er") are masked as whole words.
3.  **Spelling Correction**: Ground truth includes both the original (potentially misspelled) word and the corrected version to prevent false negatives from RAG auto-correction.

## Results & Logs

- **Real-time Progress**: Printed to console.
- **Experiment Log**: All runs are appended to `experiment_results.md`.
- **Analysis**: Run `python process_results.py` to generate `results_report.md`, which aggregates metrics like **AUC** and **Retrieval Recall**.

### Recent Findings
- **Model Performance**: `llama3` consistently outperforms `mistral` and `phi3` in mask reconstruction.
- **Retrieval Recall**: In the closed-world setting (N=500), retrieval recall is near 100% for both FAISS and BM25, indicating that the attack's success is primarily driven by the LLM's generative capability rather than retrieval failure.
