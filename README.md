# MIA-RAG-Implementation

This project implements a **Membership Inference Attack (MIA)** pipeline against **Retrieval-Augmented Generation (RAG)** systems. It evaluates whether a specific text document was part of the RAG system's knowledge base (member) or not (non-member) by analyzing the model's ability to fill in masked tokens.

## Project Structure

- `mia_rag_attack.py`: The main script that runs the ablation studies and attacks.
- `experiment_results.md`: Automatically generated log of experiment results (AUC-ROC, Accuracy, etc.).
- `CONTEXT.md`: Background context on the research (if applicable).

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

### Datasets
The project uses the HuggingFace `datasets` library to fetch real-world data:
-   **General**: `wikitext-2-raw-v1`
-   **Medical**: `pubmed_qa`
-   **Legal**: `billsum`

*Note: The first run will require an internet connection to download these datasets.*

## Results
Results are appended to `experiment_results.md` after each configuration run. The metrics include:
-   **AUC-ROC**
-   Accuracy, Precision, Recall, F1 Score
-   Confusion Matrix
