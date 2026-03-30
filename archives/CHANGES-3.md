# Product Requirements Document (PRD)
## MBA Ablation Study Expansion for Local RAG Privacy Evaluation

## 1. Executive Summary
This PRD defines the next iteration of the Mask-Based Membership Inference Attack (MBA) study for local Retrieval-Augmented Generation (RAG) systems. The current reproduction is technically successful, but the experimental design needs to be strengthened to address reviewer concerns around dataset novelty, limited ablation depth, weak reporting structure, and insufficient explanation of why local models outperform the original paper’s stronger API-based setup. These concerns are explicitly reflected in the project report comments, including the need for new datasets, broader values for **M** and **K**, dataset-specific reporting instead of global averages, and a clearer explanation of the “AUC paradox.” fileciteturn0file0L111-L127 fileciteturn0file0L151-L170

The revised study will reposition the work from a narrow reproduction into a stronger, more defensible privacy evaluation of local RAG systems. The updated scope emphasizes domain generalization, expanded ablations, better result aggregation, and a clearer framing of MBA as a practical leakage-assessment methodology for proprietary AI systems. This direction aligns with the report’s feedback to treat MBA and similar attacks as a privacy or sanitization test for deployed RAG products rather than only as a benchmark replication. fileciteturn0file0L226-L231

---

## 2. Problem Statement
The current implementation proves that a local RAG pipeline can be vulnerable to membership leakage, but the study in its present form is still too close to the reference paper in several important ways:

1. **Dataset overlap with the original paper is too high.** The current study uses HealthCareMagic, MS MARCO, and Natural Questions, which reduces novelty and weakens claims about generalization across domains. This concern is explicitly flagged in the report comments. fileciteturn0file0L111-L127
2. **The ablation grid is too shallow.** The current values for mask count (**M = 5, 10, 15**) and retrieval depth (**K = 3, 5**) are not enough to characterize where the attack breaks down or where context noise begins to function as a defense. This limitation is also directly noted in the comments on the result sections and figures. fileciteturn0file0L165-L210
3. **Result aggregation is misleading.** Reporting means across all datasets and configurations hides dataset-specific behavior and is not standard reporting practice. The comments explicitly request reporting by dataset rather than global averages. fileciteturn0file0L151-L170
4. **The explanation for unusually strong local AUC is underdeveloped.** The current report claims that local models like Llama 3 outperform the original paper’s GPT-4o-mini setup, but this requires tighter analysis tied to implementation choices such as strict reconstruction parsing, fragmented word extraction, spelling correction, and closed-world retrieval behavior. fileciteturn0file0L151-L182
5. **Some analysis sections are weak or not sufficiently justified.** In particular, the embedding/retriever synergy section is less compelling if the dataset setup remains too similar to the original paper, and the M/K analysis is currently too simple. fileciteturn0file0L183-L210

---

## 3. Project Goal
Upgrade the MBA study into a stronger academic and engineering artifact that:

- demonstrates privacy leakage across more diverse domains,
- characterizes attack behavior over a substantially wider hyperparameter space,
- reports results at the dataset level rather than through collapsed averages,
- explains why local RAG setups can produce very high AUC under constrained retrieval conditions,
- and reframes the work as a reusable privacy evaluation methodology for proprietary RAG deployments.

---

## 4. Primary Objectives

### 4.1 Scientific Objectives
- Validate whether MBA remains effective outside the original paper’s dataset trio.
- Measure how domain-specific vocabulary, formatting structure, and semantic rigidity affect leakage.
- Identify the degradation curve of attack success as masking intensity and retrieval depth change.
- Separate **retrieval success** from **generator compliance** as independent factors in attack effectiveness.

### 4.2 Engineering Objectives
- Refactor the pipeline to support plug-in dataset loaders and larger experimental sweeps.
- Run the expanded grid reliably on the available GPU VM without out-of-memory failures.
- Produce reproducible, dataset-specific reports, plots, and tables automatically.
- Make the result-processing pipeline publication-ready.

### 4.3 Framing Objectives
- Position MBA as a **RAG privacy stress test** or **sanitization benchmark** that a company could run against its own retrieval system before deployment. This explicitly follows the future-work suggestion in the report comments. fileciteturn0file0L226-L231

---

## 5. Scope

### In Scope
- Adding new datasets from domains not used in the original paper
- Expanding the search space for **M** and **K**
- Reworking result aggregation and markdown reporting
- Producing dataset-specific matrices, tables, and curves
- Tightening the analysis around retrieval recall, generator behavior, and AUC interpretation
- Improving the final narrative so the work reads as a privacy evaluation framework, not just a reproduction

### Out of Scope
- Building a full defense mechanism in this phase
- Evaluating commercial closed-source APIs beyond discussion/benchmark comparison
- Scaling beyond the controlled 500-document index unless time remains after the main ablation grid
- Replacing the entire MBA framework with a different attack family

---

## 6. Reviewer-Driven Requirements
This PRD is directly shaped by the report comments and must satisfy the following reviewer-driven requirements:

### R1. Replace or augment the current datasets
The study must stop depending solely on HealthCareMagic, MS MARCO, and Natural Questions. At least two new domains must be added so that the work demonstrates genuine domain generalization. fileciteturn0file0L111-L127

### R2. Expand the hyperparameter study
The attack analysis must include more values for **M** and **K** so the study can reveal failure points, degradation slopes, and distractor effects more convincingly. fileciteturn0file0L165-L210

### R3. Report results by dataset
All summary tables and plots must be dataset-specific. Global averages across datasets must be deprecated or clearly secondary. fileciteturn0file0L151-L170

### R4. Better justify unexpectedly strong local performance
The report must clearly explain why local models can yield very high AUC despite being weaker than GPT-4o-mini overall, including the role of implementation refinements and closed-world retrieval. fileciteturn0file0L151-L182

### R5. Improve or remove weak subsections
Sections such as embedding/retriever synergy should only remain if supported by the new dataset design and stronger analysis. Weak sections should be reworked rather than kept for completeness. fileciteturn0file0L183-L193

---

## 7. Updated Experimental Design

## 7.1 Dataset Strategy
The revised study must include domains that are structurally different from the original paper’s corpora.

### Required New Domains
#### A. Financial / Legal Domain
Candidate datasets:
- **FiQA** for finance-oriented question-answer or passage retrieval
- **LexGLUE-derived text subsets** for legal language
- other compact finance/legal corpora that can be normalized into a 500-document retrieval index

**Purpose:** These datasets contain rigid, specialized vocabulary and may produce stronger or weaker leakage depending on term specificity and phrasing regularity.

#### B. Academic / Technical Domain
Candidate datasets:
- **ArXiv abstracts** from a focused subject area
- **technical documentation corpora** such as framework or library documentation
- curated domain docs with structured headings, code-adjacent terminology, and repeated technical jargon

**Purpose:** These datasets test whether MBA behaves differently when documents are concise, template-like, and structurally repetitive.

### Optional Retained Domains
The original datasets may still be kept as comparison baselines, but they must no longer dominate the narrative. If retained, they should be framed as **reference baselines** rather than the core novelty.

### Dataset Constraints
Each dataset must be transformed into a uniform experimental format:
- fixed index size target: **500 documents** per dataset for the main controlled comparison,
- consistent cleaning and chunking rules,
- comparable member/non-member split strategy,
- standardized document length filters,
- consistent masking and evaluation protocol.

### Acceptance Criteria
- At least **2 new datasets** added and fully integrated.
- All datasets produce clean member/non-member evaluation sets.
- Preprocessing is documented and reproducible.

---

## 7.2 Hyperparameter Grid Expansion
The ablation study must move from a shallow comparison to a proper sensitivity analysis.

### Mask Count (M)
Current grid is too narrow. The revised grid will be:

```text
M ∈ {1, 3, 5, 7, 10, 15, 20}
```

**Reason:** This allows the study to observe:
- low-mask signal quality,
- mid-range sweet spots,
- and high-mask context destruction.

### Retrieval Depth (K)
The revised grid will be:

```text
K ∈ {1, 3, 5, 10, 15}
```

**Reason:** This enables analysis of:
- single-document retrieval,
- moderate distractor exposure,
- and extreme noise conditions where extra retrieved context may weaken reconstruction.

### Optional Secondary Sweeps
If compute allows, add:
- different index sizes, e.g. **N ∈ {500, 1000}**,
- different mask-selection heuristics,
- different query construction variants,
- threshold sensitivity for the BMIC decision stage.

These are optional and only start after the main M/K expansion is complete.

### Acceptance Criteria
- Full M/K grid runs successfully for all required datasets and core model/retriever combinations.
- No silent skipping of failed runs.
- All failures are logged with clear reasons.

---

## 7.3 Core Experimental Matrix
The base experiment matrix should remain manageable but strong enough for analysis.

### Models
- Llama 3
- Mistral
- Phi-3

### Retrievers
- FAISS (dense)
- BM25 (sparse)

### Embeddings
- all-MiniLM-L6-v2
- bge-small-en-v1.5

### Controlled Settings
- Index size: 500 documents
- Evaluation set: 50 members / 50 non-members per dataset, unless a dataset requires a justified modification

### Priority Order
1. Llama 3 across all datasets and expanded M/K
2. Mistral across all datasets and expanded M/K
3. Phi-3 where feasible, especially to analyze generator compliance failure
4. Retriever/embedding comparisons once the dataset-generalization story is strong enough to justify them

---

## 8. Reporting and Analytics Requirements

## 8.1 Aggregation Rules
The global “Average AUC” must no longer be the main reporting unit. The result-processing pipeline must enforce the following hierarchy:

1. **Dataset-level reporting first**
2. Within dataset: model comparisons
3. Within dataset: retriever and embedding comparisons
4. Within dataset: M/K sensitivity analysis
5. Global averages only as supplementary appendix summaries, if included at all

This directly addresses the report comment that averaging across datasets and configurations is not standard practice and hides meaningful behavior. fileciteturn0file0L151-L170

## 8.2 Required Output Tables
For each dataset, automatically generate:

- **Table A:** AUC by model
- **Table B:** Retrieval recall by model
- **Table C:** AUC matrix for M × K
- **Table D:** Best and worst configurations
- **Table E:** Retriever × embedding comparison

## 8.3 Required Plots
For each dataset, generate:

- line plot: AUC vs. M for fixed K values
- line plot: AUC vs. K for fixed M values
- heatmap: M × K AUC matrix
- bar chart: model comparison
- optional bar chart: retrieval recall vs. attack AUC

## 8.4 Required Narrative Analysis
The report must answer these questions for each dataset:

1. Does the attack remain effective in this domain?
2. Which model leaks the most and why?
3. Does increased retrieval depth help or hurt leakage?
4. At what mask count does context destruction begin?
5. Is retrieval the bottleneck, or is generator compliance the bottleneck?
6. Does embedding/retriever choice materially matter in this domain?

---

## 9. AUC Paradox Analysis Requirement
A dedicated subsection must be added to explain why local models can produce stronger AUC than the original paper’s GPT-4o-mini setup, despite being weaker general-purpose models.

### Required Explanatory Factors
The analysis must explicitly discuss:

#### 1. Fragmented Word Extraction
If the masking pipeline reconstructs fragmented words more faithfully than the original setup, this can reduce false negatives and improve AUC.

#### 2. Spelling Correction / Parsing Robustness
If the scoring pipeline tolerates formatting variation or spelling correction better, the local pipeline may receive cleaner reconstruction signals.

#### 3. Closed-World Retrieval Conditions
The report already states that a 500-document index yielded effectively perfect retrieval recall. This must be reframed as a major reason for the inflated attack performance: the problem becomes less about finding the document and more about whether the generator can copy or reconstruct from it. fileciteturn0file0L173-L182

#### 4. Generator Compliance vs. Model Size
The Phi-3 result already suggests that strong attack performance depends heavily on instruction-following fidelity rather than raw model capability. This point should be expanded and supported with examples or failure counts. fileciteturn0file0L173-L182

### Acceptance Criteria
- The final report contains a standalone subsection on this paradox.
- The explanation is backed by both metric evidence and concrete implementation behavior.

---

## 10. Codebase Refactoring Requirements

## 10.1 `mia_rag_attack.py`
### Required Changes
- Add modular dataset loader interfaces.
- Add preprocessing hooks for dataset-specific normalization.
- Replace hardcoded dataset assumptions with configuration-driven dataset selection.
- Expand config schema to accept iterable M and K lists.
- Add better logging for per-run metadata:
  - dataset
  - model
  - retriever
  - embedding
  - M
  - K
  - recall
  - AUC
  - runtime
  - failure reason if any
- Add GPU-conscious batching or staged execution where possible.

### Nice to Have
- resumable experiment execution,
- cached intermediate outputs,
- batched evaluation for repeated query/model settings.

## 10.2 `process_results.py`
### Required Changes
- Remove or downgrade global average metrics.
- Group results by dataset before all other summaries.
- Generate dataset-specific markdown sections automatically.
- Output M × K matrices per dataset.
- Output best/worst configuration tables per dataset.
- Validate missing values and incomplete runs before report generation.

### Nice to Have
- export CSV + Markdown + JSON summary bundles,
- produce publication-ready plot images automatically.

---

## 11. Functional Requirements

### FR1. Dataset Loader Abstraction
The system shall support adding a new dataset through a dedicated loader without modifying core attack logic.

### FR2. Configurable Experimental Sweeps
The system shall allow M and K to be passed as configurable lists from a single experiment config.

### FR3. Dataset-First Reporting
The system shall group all outputs by dataset before any cross-dataset comparison.

### FR4. Automatic Matrix Generation
The system shall generate M × K result matrices for every dataset-model combination.

### FR5. Failure Logging
The system shall log OOMs, parse failures, retrieval failures, and generation-format failures explicitly.

### FR6. Reproducible Exports
The system shall save raw run results and processed summaries in reproducible machine-readable formats.

---

## 12. Non-Functional Requirements

### NFR1. Reproducibility
Every experimental run must be traceable through config files, fixed seeds where possible, and exported metadata.

### NFR2. Scalability
The pipeline must support larger sweeps on the GPU VM without requiring major code changes.

### NFR3. Robustness
The result processor must not fail silently when partial runs are missing.

### NFR4. Clarity
The generated markdown report must be readable enough to directly support the final paper-writing stage.

---

## 13. Risks and Mitigations

### Risk 1: GPU OOM during expanded grid
**Mitigation:** add batched execution, sequential scheduling, optional reduced concurrency, and resumable run checkpoints.

### Risk 2: New datasets break preprocessing assumptions
**Mitigation:** introduce dataset validation scripts and document-length checks before running the full experiment.

### Risk 3: Report becomes too broad
**Mitigation:** prioritize dataset generalization, M/K ablation, and AUC explanation first. Secondary analyses only stay if they are strong enough.

### Risk 4: Embedding/retriever analysis remains weak
**Mitigation:** keep this section only if the new datasets reveal meaningful cross-domain differences. Otherwise shrink it or move it to an appendix.

---

## 14. Success Metrics
The update is considered successful when all of the following are true:

### Experimental Success
- Expanded M/K grid completes for the required datasets and core models.
- No critical OOM failures block the main comparison matrix.
- At least 2 new datasets are fully integrated and evaluated.

### Reporting Success
- `results_report.md` is grouped by dataset.
- M × K matrices are generated for each dataset.
- Curves clearly show where the attack strengthens, plateaus, and degrades.
- Global average AUC is no longer the main headline metric.

### Research Success
- The revised report clearly explains the local AUC paradox.
- The study demonstrates domain-dependent leakage behavior.
- The work reads as a stronger privacy-evaluation framework, not just a reproduction.

---

## 15. Phased Implementation Roadmap

## Phase 1 — Refactor Foundation
- modularize dataset loading
- expand config schema for M/K sweeps
- clean result logging format
- verify current datasets still run end-to-end

## Phase 2 — Add New Datasets
- integrate financial/legal dataset
- integrate academic/technical dataset
- normalize preprocessing and document count
- validate member/non-member split construction

## Phase 3 — Run Main Ablation Grid
- run priority experiments with Llama 3 first
- expand to Mistral and Phi-3
- monitor runtime, memory, and failure cases
- cache and checkpoint outputs

## Phase 4 — Rebuild Reporting Pipeline
- dataset-first aggregation
- M × K heatmaps and markdown tables
- best/worst configuration summaries
- retrieval vs. generation bottleneck analysis

## Phase 5 — Final Analysis and Write-Up
- write AUC paradox subsection
- tighten discussion on domain effects
- decide whether embedding/retriever synergy stays in main body
- frame the overall work as RAG privacy stress testing

---

## 16. Immediate Action Checklist

### Code
- [ ] Refactor `MIAConfig` to accept list-based M and K values
- [ ] Add dataset loader interface
- [ ] Implement first new dataset loader
- [ ] Implement second new dataset loader
- [ ] Add structured logging for every run

### Experiments
- [ ] Validate one mini-run for each new dataset
- [ ] Run Llama 3 on the expanded M/K grid first
- [ ] Check VRAM usage and runtime profile
- [ ] Add resume/checkpoint support if needed

### Reporting
- [ ] Remove primary dependence on global mean AUC
- [ ] Build dataset-specific summary tables
- [ ] Generate M × K heatmaps
- [ ] Draft the AUC paradox explanation section
- [ ] Reframe conclusion toward privacy auditing / sanitization testing

---

## 17. Final Deliverables
- Updated experimental codebase
- New dataset loader modules
- Expanded raw result files
- Revised `process_results.py`
- Dataset-specific `results_report.md`
- Plot bundle for M/K sensitivity and model comparisons
- Updated paper sections aligned with reviewer comments

---

## 18. Final Positioning Statement
This expanded study should no longer present itself as only a reproduction of Liu et al. Instead, it should present itself as a controlled, local, reproducible privacy evaluation framework for RAG systems. The core value is not just showing that MBA works, but showing **when**, **why**, and **under what domain and system conditions** it becomes most dangerous for proprietary knowledge bases. That framing is the strongest way to answer the report feedback and make the project more defensible academically and more useful practically. fileciteturn0file0L226-L231