# Mask-Based Membership Inference Attack (MBA) Implementation

This repository contains the implementation of the **Mask-Based Membership Inference Attack (MBA)** framework for Retrieval-Augmented Generation (RAG) systems, as described in *Liu et al. (2025)*.

## Project Structure

- `mia_rag_attack.py`: The main script implementing the MBA attack, utilizing Fragmented Word Extraction, Spelling Correction, and Adjacency Filtering.
- `requirements.txt`: Python dependencies.
- `LOGS.md`: Project change log.
- `scripts-deprecated/`: Old iterations of the attack scripts.

## Prerequisites

1.  **Python 3.10+**
2.  **Ollama**: You must have Ollama installed and running to serve the LLM (e.g., Llama 3, Phi-3).
    - [Download Ollama](https://ollama.com/)
    - Pull the model you intend to use:
      ```bash
      ollama pull llama3
      ```

## Installation

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: If you have a GPU, ensure you have the correct version of PyTorch installed for your CUDA version.*

2.  **Verify Ollama**:
    Ensure Ollama is running in the background (`ollama serve`).

## Usage

To run the attack with default settings (HealthCareMagic dataset, Llama 3):

```bash
python mia_rag_attack.py
```

### Configuration

You can customize the attack by modifying the `MIAConfig` class at the bottom of `mia_rag_attack.py` or by editing the script parameters directly.

**Key Parameters:**

- `dataset_type`:
    - `"healthcaremagic"`: (Default) Medical conversations (Liu et al., 2025).
    - `"msmarco"`: General knowledge (Validation set).
    - `"nq"`: Natural Questions (Simplified).
- `llm_model`: The Ollama model name (e.g., `"llama3"`, `"phi3"`, `"mistral"`).
- `masking_strategy`:
    - `"hard"`: Uses the Proxy Model (GPT-2) to mask difficult words.
    - `"random"`: Randomly masks words (Baseline).
- `num_masks`: Number of words to mask per document (Default: 5).

### Example: Running with Phi-3 on MS-MARCO

Open `mia_rag_attack.py` and modify the `__main__` block:

```python
config = MIAConfig(
    llm_model="phi3", 
    dataset_type="msmarco",
    masking_strategy="hard",
    num_masks=5
)
```

## How It Works

1.  **Data Loading**: Loads specific datasets used in the research paper.
2.  **Masking**:
    - **Fragmented Word Extraction**: Ensures words split by tokenizers are masked as a whole.
    - **Ranking**: simple GPT-2 loss ranking or Random selection.
    - **Refinement**: Fixes spelling errors in ground truth and prevents adjacent masking.
3.  **RAG Query**:
    - The masked text is sent to the RAG system.
    - The RAG system retrieves documents (Top-K) and attempts to fill the masks.
4.  **Evaluation**:
    - **Mask Accuracy**: Accuracy of filled masks.
    - **Retrieval Recall**: Did the RAG actually find the source document?
    - **AUC**: Area Under the ROC Curve to measure membership inference success.

## Results

Results are logged to:
- Console Output (Real-time progress)
- `experiment_results.md` (Summary of runs)
