## [2026-01-25 18:27:10.297493] - Major Overhaul of `mia_rag_attack.py`

### Feature Implementation: Mask-Based Membership Inference Attack (MBA)
We have completely rewritten the attack script to strictly adhere to the methodology described in *Liu et al., 2025*.

#### 1. Methodological Alignments
- **Fragmented Word Extraction**: Implemented Algorithm 2 from the paper. The tokenizer now identifies words split into multiple sub-tokens (e.g., "canestan" -> "can", "est", "an") and treats them as atomic units for masking.
- **Spelling Correction Strategy**: Integrated `oliverguhr/spelling-correction-english-base`.
    - **Logic**: If a masked word is misspelled in the original text, the ground truth now includes *both* the original misspelled word and the corrected version. This prevents the RAG system's auto-correction from falsely triggering a "wrong" prediction.
- **Adjacency Filtering**: Implemented a constraint in the masking ranking (Top-M) to ensure no two masked words are adjacent to one another.
- **Datasets Updated**: Now using the specific datasets from the paper:
    - **Medical**: `RafaelMPereira/HealthCareMagic-100k-Chat-Format-en`
    - **General**: `ms_marco` (Validation Set) & `LLukas22/nq-simplified`
    - Removed: `wikitext`, `pubmed_qa`, `billsum`.

#### 2. Stability & Infrastructure Fixes
- **CUDA Crash Resolution (Legal Dataset)**: Implemented strict token truncation (`max_length=512`) during the RAG vector store ingestion. This resolves the `device-side assert triggered` errors caused by long documents exceeding the embedding model's context window.
- **Transformer Logging**: Suppressed verbose transformer warnings to clean up console output.

#### 3. New Metrics & Evaluation
- **Retrieval Recall**: Added a metric to track whether the target document was actually present in the top-k retrieved chunks. This helps distinguish between *retrieval failures* and *generation failures*.
- **Robust Evaluation**: The script now supports a configurable `masking_strategy` ("hard" vs "random") to establish a proper baseline.

#### 4. Model Specifics
- **Phi-3 Support**: Added specific prompt templates (One-Shot) for Phi-3 and smaller models that struggle with zero-shot JSON formatting.

# Project Change Log
## [2026-01-25 23:27:10.297493] - Research Methodology Updates & Optimization

### 1. Expanded Ablation Studies
We have significantly expanded the `mia_rag_attack.py` script to perform a comprehensive grid search across multiple RAG components.
- **LLMs**: `llama3`, `mistral`, `phi3`
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`, `BAAI/bge-small-en-v1.5`
- **Retrievers**: `faiss` (Dense Vector Search) and `bm25` (Keyword Search via `rank_bm25`)

### 2. Experimental Optimization (Index vs. Eval Decoupling)
To solve the issue of trivial Retrieval Recall (100%) due to small index sizes, while keeping runtime manageable, we decoupled the RAG Index size from the Evaluation sample size.
- **Index Size (`index_size`)**: Defaulted to `500`. This creates a larger "haystack", making the retrieval task realistically difficult.
- **Eval Size (`eval_size`)**: Defaulted to `50`. We sub-sample 50 documents from the index to run the expensive LLM generation and attack metrics.
- **Benefit**: Provides realistic retrieval metrics without requiring days of compute time.

### 3. Bug Fixes & Improvements
- **Regex Syntax**: Fixed invalid escape sequences in metric evaluation regex.
- **Config Management**: Resolved duplicate arguments in `MIAConfig`.
- **Dependency Handling**: Added `rank_bm25` support with proper error messaging if missing.

### 4. Experimental Observations regarding "Retrieval Recall"
We observed a consistent **1.0000 (100%) Retrieval Recall** across experiments. This is expected behavior due to:
- **Small Closed-World Index**: Even with `index_size=500`, the search space is essentially "easy" for modern vector DBs compared to million-scale production databases.
- **High Vector Similarity**: A "masked" query (only ~5 words missing) creates an embedding extremely similar to the original document embedding.
- **Conclusion**: Retrieval is not the bottleneck for MIA in this specific setup; the attack performance is driven primarily by the LLM's reconstruction ability.

## [2026-01-26] - Ablation Study Completion & Results Analysis

### 1. Results Processing Infrastructure
- **Updated `process_results.py`**: Rewrote the parsing logic to handle the new bullet-point log format in `experiment_results.md`.
- **New Metrics Integration**:  The script now generates reports based on `AUC` and `Retrieval Recall` instead of legacy classification metrics.

### 2. Key Findings from Full Grid Search (36 Experiments)
- **Model Dominance**: `llama3` consistently outperformed other models, achieving AUC scores >0.99 on the HealthcareMagic dataset.
- **Model Instability**: `phi3` showed significant instability, failing to perform better than random guessing (AUC 0.50) in several configurations, likely due to difficulties in following the strict JSON output format for mask reconstruction.
- **Dataset Difficulty**:
    - **Easiest**: `healthcaremagic` (Medical)
    - **Hardest**: `nq` (Natural Questions)
- **Retrieval Recall Confirmation**: All 36 runs confirmed a 100% Retrieval Recall, validating our hypothesis that in a closed-world setting (N=500), retrieval is trivial for both FAISS and BM25.

### 3. Artifact Generation
- Generated `results_report.md`: A comprehensive markdown report summarizing the best configurations and aggregating performance by Model, Retriever, and Dataset.

