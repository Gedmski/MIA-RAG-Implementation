# Proposal for Project Refinement: Mask-Based Membership Inference Attack (MBA)

**Date:** January 25, 2026
**Subject:** Critical Methodological Alignments and Stability Fixes for MBA Implementation

## 1. Executive Summary
Following a review of the initial experimental logs (`experiment_failures.txt`, `experiment_results.md`) and a detailed comparison with the source paper *"Mask-based Membership Inference Attacks for Retrieval-Augmented Generation" (Liu et al., 2025)*, we have identified substantial deviations in the current implementation.

While the current Llama-3 implementation achieves an AUC of 1.0, this "perfect" score suggests trivial exact-match retrieval rather than robust semantic inference. Furthermore, severe CUDA instabilities were observed on the Legal dataset. This proposal outlines the necessary changes to strictly adhere to the paper's algorithms (specifically dealing with tokenization and spelling) and to resolve the crash-inducing technical constraints.

---

## 2. Critical Stability Fixes (Priority 1)

**Issue Identified:**
The `experiment_failures.txt` log reports repeated `CUDA error: device-side assert triggered` failures, specifically on **Legal** datasets using `sentence-transformers/all-MiniLM-L6-v2`.
**Root Cause:**
Legal documents (BillSum) are lengthy. The embedding models utilized have a hard limit (typically 512 tokens). When documents exceed this limit without truncation, the index lookup fails on the GPU, causing the device-side assertion error.

**Proposed Implementation:**
We must implement explicit token truncation during the **RAG Vector Store Ingestion** phase, consistent with the paper's handling of document chunks.

*   **Action:** Modify the embedding generation pipeline to enforce `truncation=True` and `max_length=512`.
*   **Rationale:** This will resolve the crash loop on the Legal dataset and allow the ablation study to complete for all domains.

---

## 3. Methodological Alignment with Research Paper

The current implementation uses a simplified probability ranking for masking. To reproduce the paper's validity, we must implement the specific heuristics defined in the authors' **Mask Generation Algorithm (Algorithm 4)**.

### 3.1. Implement "Fragmented Word Extraction"
**Current State:** The proxy model masks words based solely on probability.
**Paper Requirement:** The paper notes that tokenizers often split complex words (e.g., "canestan" $\rightarrow$ "can", "est", "an"). Masking only part of a word confuses the attack.
**Proposed Change:**
*   Implement **Algorithm 2** from the paper.
*   Scan for consecutive tokens without whitespace and treat them as a single unit.
*   If a fragmented word is selected for masking, **all** constituent tokens must be masked together.

### 3.2. Implement "Misspelled Word Correction"
**Current State:** No spelling checks are performed.
**Paper Requirement:** The paper highlights that LLMs will "fix" typos rather than predict them. If the original document has a typo (e.g., "nearlt"), and we mask it, the RAG might retrieve the doc but generate the correct spelling "nearly," leading to a mismatch in our scoring.
**Proposed Change:**
*   Implement **Algorithm 1**.
*   Integrate the `oliverguhr/spelling-correction-english-base` model (as specified in).
*   **Logic:** If a masked word is misspelled, add *both* the original misspelled word and the corrected version to the "Ground Truth" answer set. If the RAG predicts either, it counts as a success.

### 3.3. Adjacency Filtering
**Current State:** Top $M$ hard words are masked, potentially selecting adjacent words.
**Paper Requirement:** Masking adjacent words (e.g., "[MASK] [MASK]") causes the LLM to lose track of how many words to generate.
**Proposed Change:**
*   Add a constraint to the `rank_words` function: If word $i$ is masked, word $i+1$ and $i-1$ cannot be masked, regardless of their difficulty rank.

---

## 4. Addressing "Too Good To Be True" Results (Validity)

**Issue Identified:**
Our logs show **AUC = 1.0000** for Llama-3 on General and Medical datasets. This indicates the task is currently trivial—likely due to exact string matching between the masked query and the database document.

**Proposed Change: Paraphrasing & Robustness Checks**
To ensure we are measuring *membership inference* and not just *string matching*, we should implement the **Defense Strategies** analyzed in the paper.

*   **Action:** Implement a **Paraphrasing** step for the input query.
*   **Logic:** Before feeding the masked text to the RAG, slightly paraphrase the surrounding context (unmasked parts).
*   **Expected Outcome:** AUC should drop from 1.0 to a realistic range (0.85–0.95), proving the attack works based on semantic information recovery as claimed in the paper.

---

## 5. Metric & Baseline Expansion

To strictly follow the paper's evaluation protocol, we need to expand our metrics beyond simple Accuracy/AUC.

### 5.1. Retrieval Recall
**Paper Reference:** The paper introduces "Retrieval Recall" to verify if the RAG actually found the document.
**Implementation:**
*   Modify the retriever to return the IDs of the retrieved chunks.
*   **Metric:** check if `Target_Document_ID` is present in `Retrieved_IDs`.
*   This will help diagnose why **Phi-3** is failing (AUC 0.54)—is it failing to retrieve, or failing to generate?

### 5.2. Random Baseline
**Paper Reference:** The paper compares the "Hard Word" attack against a "Random Masking" baseline.
**Implementation:**
*   Add a `masking_strategy` parameter to the pipeline.
*   Run a full experiment set where masks are chosen randomly (excluding stop words).
*   **Goal:** Demonstrate that the "Proxy Model" approach yields a higher AUC than random guessing.

---

## 6. Model-Specific Optimization (Phi-3)

**Issue:** Phi-3 performed near random guessing (AUC 0.54).
**Hypothesis:** Smaller models struggle with complex JSON-like output formatting instructions.
**Proposed Change:**
*   Review the prompt template against **Figure 5** in the paper.
*   For Phi-3 specifically, simplify the system prompt to use a one-shot example (providing an example of a masked input and the expected output format) to enforce compliance.

---

### Summary of Action Plan

1.  **Fix:** Add `truncation=True` to Embedding loading (resolves CUDA crashes).
2.  **Code:** Implement `FragmentedWordExtraction` and `AdjacencyFilter`.
3.  **Code:** Integrate `spelling-correction-english-base` model.
4.  **Evaluate:** Add "Random" baseline run.
5.  **Metric:** Log `Retrieval_Recall` to debug Phi-3 performance.

Implementing these changes will transition the project from a basic proof-of-concept to a rigorous reproduction of the Liu et al. (2025) research.