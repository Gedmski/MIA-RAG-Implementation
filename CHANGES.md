# Expanding the MBA Grid Search (Option A)

This guide outlines the steps to inject the mathematical hyperparameters (`num_masks` and `retriever_k`) into your existing ablation pipeline. This satisfies the requirement to test the attack's sensitivity to mask volume and retrieval depth.

## 1. Update `MIAConfig` in `mia_rag_attack.py`

First, expose `retriever_k` in your configuration class so it can be dynamically assigned during the grid search.

```python
from dataclasses import dataclass

@dataclass
class MIAConfig:
    dataset_type: str = "healthcaremagic"
    llm_model: str = "llama3"
    retriever_type: str = "faiss"
    embedding_model: str = "all-MiniLM-L6-v2"
    masking_strategy: str = "hard"
    num_masks: int = 5          # Already exists, just needs to be varied
    retriever_k: int = 3        # NEW: Expose K for the retriever
    index_size: int = 500
    eval_size: int = 50

```

## 2. Update Retriever Instantiation

Locate the function or method where you instantiate FAISS and BM25. Ensure they accept and apply `config.retriever_k` instead of a hardcoded value.

```python
# Example for LangChain retriever setup
retriever = vectorstore.as_retriever(search_kwargs={"k": config.retriever_k})

```

## 3. Expand the Grid Search Loop

In the `__main__` execution block of `mia_rag_attack.py`, add the new hyperparameter arrays to your grid search logic. Note that expanding these dimensions will significantly increase the total number of experiment runs (e.g., adding 3 `M` values and 2 `K` values multiplies your total runs by 6).

```python
import itertools

if __name__ == "__main__":
    # Existing dimensions
    datasets = ["healthcaremagic", "msmarco", "nq"]
    llms = ["llama3", "mistral", "phi3"]
    embeddings = ["all-MiniLM-L6-v2", "bge-small-en-v1.5"]
    retrievers = ["faiss", "bm25"]
    
    # NEW: Mathematical Hyperparameters
    num_masks_list = [5, 10, 15]   # Testing M
    retriever_k_list = [3, 5]      # Testing K

    # Generate all combinations
    experiments = list(itertools.product(
        datasets, llms, embeddings, retrievers, num_masks_list, retriever_k_list
    ))

    print(f"Starting Grid Search: {len(experiments)} total configurations.")

    for (dataset, llm, emb, ret, m, k) in experiments:
        config = MIAConfig(
            dataset_type=dataset,
            llm_model=llm,
            embedding_model=emb,
            retriever_type=ret,
            num_masks=m,
            retriever_k=k,
            index_size=500,
            eval_size=50
        )
        
        # Call your existing pipeline execution function here
        # run_experiment(config)

```

## 4. Addressing the Threshold Fraction (`y`)

You do not need to add `y` to the grid search. Because your evaluation pipeline calculates the continuous Area Under the Curve (AUC) for the Receiver Operating Characteristic (ROC), it is already mathematically evaluating the performance across *all possible* classification thresholds. You can state this directly in your report to defend its omission from the ablation variables.

## 5. Updates for `README.md`

Add the new parameters to your Configuration table to ensure the documentation reflects the new system capabilities.

| Parameter | Options / Description | Default |
| --- | --- | --- |
| `num_masks` | Number of words to mask per document (Testing `5`, `10`, `15`) | `5` |
| `retriever_k` | Number of documents retrieved by RAG (Testing `3`, `5`) | `3` |

Update the "Usage" section to reflect the expanded scope:

```markdown
**This will run 216+ experiments** iterating through:
- **Datasets**: `healthcaremagic`, `msmarco`, `nq`
- **LLMs**: `llama3`, `mistral`, `phi3`
- **Embeddings**: `all-MiniLM-L6-v2`, `bge-small-en-v1.5`
- **Retrievers**: `faiss` (Dense), `bm25` (Sparse)
- **Masks (M)**: `5`, `10`, `15`
- **Retrieved Docs (K)**: `3`, `5`

```