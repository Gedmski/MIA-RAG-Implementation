# PRD: Lean Ablation Study YAML Configuration for MBA-on-RAG

## 1. Objective

Create a **lean, publication-defensible experiment configuration** for the MBA-on-RAG project that:

1. avoids a wasteful full Cartesian sweep,
2. isolates major factors cleanly,
3. includes a **GPT model** for comparison since experiments will run on a VM,
4. extends the study with **new datasets** and **new hyperparameters** not properly addressed in the current write-up,
5. remains compatible with the repo’s YAML-driven experiment runner. 

---

## 2. Problem

The current experimental setup risks turning the study into a **massive combinatorial sweep** instead of a proper ablation study.

A full sweep across:

* datasets,
* models,
* retrievers,
* embeddings,
* `M`,
* `K`,
* and possibly `γ`, seeds, or sample-size variants

can explode into thousands of runs. That is expensive and also weakens interpretability because too many factors vary at once.

The original MBA paper did not just vary everything blindly. It had:

* a main setup,
* ablation baselines,
* parameter studies for `M` and `γ`,
* and a note that the method is relatively insensitive to `K` in their setup. 

This PRD defines a **lean experimental plan** that preserves scientific value while drastically reducing runtime.

---

## 3. Goals

### Primary goals

* Produce a YAML config structure for **staged ablations**, not a monolithic full sweep.
* Add **GPT-4o-mini** as an evaluation model to compare with local models, since the original paper used it as the main black-box LLM. 
* Include **new datasets** beyond the original three, which your repo already supports through YAML defaults such as **FiQA** and **ArXiv**. 
* Add underexplored hyperparameters and system variables.

### Secondary goals

* Keep runtime manageable.
* Improve paper defensibility by clearly separating:

  * baseline reproduction,
  * lean ablations,
  * robustness checks,
  * optional extended sweeps.

---

## 4. Non-goals

* This config is **not** meant to exhaust every possible combination.
* This config is **not** a benchmark leaderboard script.
* This config is **not** intended to reproduce every appendix result from the paper.

---

## 5. Research framing

The original paper’s key tunable variables include:

* **number of masks `M`**,
* **membership threshold `γ`**,
* **retrieval depth `K`** as a system parameter,
* model/retrieval/embedding choices,
* and dataset choice. 

Your revised study should frame the experiments as:

1. **Baseline reproduction**
2. **Lean factor-isolation ablations**
3. **Cross-dataset robustness validation**
4. **Model-family comparison including GPT**

That makes the study much cleaner than “everything crossed with everything.”

---

## 6. Lean ablation design

## 6.1 Baseline configuration

Define one fixed baseline:

* dataset: `healthcaremagic`
* model: `gpt-4o-mini`
* retriever: `faiss`
* embedding: `bge-small-en-v1.5`
* `M = 10`
* `K = 5`
* `γ = 0.5`
* index size: fixed
* evaluation size: fixed
* seed: fixed

Why:

* `gpt-4o-mini` matters because the original paper used it as the main black-box LLM. 
* `M = 10` is inside the original paper’s strong operating region. They found performance was generally good when `M` was between 5 and 15. 
* `γ = 0.5` is a reasonable anchor since the paper found performance fairly stable around 0.5–0.7. 
* `K = 5` is more practical than `K = 10` for your lean study and lets you test distractor sensitivity.

---

## 6.2 Core lean ablations

### Ablation A — LLM family

Hold everything fixed except model.

Models:

* `gpt-4o-mini`
* `llama3`
* `mistral`
* `phi3`

Purpose:

* compare hosted GPT vs local open models,
* test whether instruction-following drives attack success more than raw retrieval,
* directly answer reviewer criticism around missing GPT comparison.

### Ablation B — mask count `M`

Hold everything fixed except `M`.

Values:

* `M ∈ {3, 5, 10, 15, 20}`

Why expand:

* the original paper used `{5,10,15,20}`. 
* adding `3` helps test low-mask instability and error tolerance.

### Ablation C — threshold `γ`

Hold everything fixed except `γ`.

Values:

* `γ ∈ {0.3, 0.5, 0.7, 0.9}`

Why:

* the original paper tuned `γ` from 0.1 to 1.0 and concluded performance is relatively stable around 0.5–0.7. 
* a lean study does not need 10 threshold values.

### Ablation D — retrieval depth `K`

Hold everything fixed except `K`.

Values:

* `K ∈ {1, 3, 5, 10}`

Why:

* the paper discussed `K` as important but did not foreground it in the main study. 
* `K=1` and `K=3` test low-noise retrieval,
* `K=10` aligns with the original main setup.

### Ablation E — retriever/embedding stack

Hold model and dataset fixed, vary retrieval stack.

Retrievers:

* `faiss`
* `bm25`

Embeddings:

* `bge-small-en-v1.5`
* `all-minilm-l6-v2`

Purpose:

* isolate dense vs sparse retrieval,
* test whether embedding choice affects leakage signal.

---

## 6.3 Cross-dataset robustness set

Use a **reduced model set**, not all models.

Datasets:

* `healthcaremagic`
* `msmarco`
* `nq`
* `fiqa`
* `arxiv`

Why:

* the original paper only used three QA datasets: HealthCareMagic-100k, MS-MARCO, and NQ-simplified. 
* your repo already supports **FiQA** and **ArXiv**, which are strong additions:

  * **FiQA** gives financial-domain text
  * **ArXiv** gives scientific/technical abstracts 

Recommended robustness models:

* `gpt-4o-mini`
* `llama3`

That is enough. No need to drag Phi-3 through every dataset if it underperforms badly.

---

## 7. Proposed new hyperparameters and factors not properly addressed

These are the ones worth adding.

## 7.1 Seeds / repeated trials

Add:

* `seed ∈ {42, 1337, 2026}`

Why:

* current results may be too dependent on one sample split or retrieval index state.
* this makes the study more defensible.

## 7.2 Index size

Add:

* `index_size ∈ {500, 2000, 10000}`

Why:

* your current setup seems small and may artificially inflate recall and AUC.
* the original paper used much larger datasets and training/testing splits than a tiny local sample. 
* this addresses “closed-world toy index” criticism.

## 7.3 Evaluation set size

Add:

* `eval_members = eval_non_members ∈ {50, 100, 250}`

Why:

* tiny evaluation samples make metrics noisy.
* lets you measure stability vs cost.

## 7.4 Chunking strategy

Add:

* `chunk_size ∈ {none, 256, 512}`
* `chunk_overlap ∈ {0, 32, 64}`

Why:

* real RAG systems are chunked.
* chunking strongly affects whether the full target evidence survives retrieval.

## 7.5 Retriever search type / ANN params

For FAISS/HNSW:

* `faiss_metric ∈ {inner_product, cosine}`
* `hnsw_ef_search ∈ {32, 64, 128}`

Why:

* the original paper used HNSW in FAISS with inner product. 
* search aggressiveness can alter recall and downstream attack success.

## 7.6 Prompt strictness

Add:

* `prompt_variant ∈ {strict_format, strict_format_with_examples, concise}`

Why:

* instruction adherence is a major driver of attack success.
* this is especially relevant for comparing GPT vs local models.

## 7.7 Proxy language model

Add:

* `proxy_model ∈ {gpt2-xl, gpt2-large}`

Why:

* the original paper used `gpt2-xl` as the proxy LM. 
* checking a smaller proxy can show whether proxy capacity materially affects mask selection quality.

## 7.8 Mask selection policy

Add:

* `mask_policy ∈ {proxy_ranked, random, llm_generated, proxy_ranked_no_spell_correct}`

Why:

* this mirrors the original ablation logic more closely. The paper explicitly compared random masking, LLM-based masking, proxy-LM-only, and no spelling-correction variants. 

## 7.9 Membership decision rule

Add:

* `decision_rule ∈ {threshold_gamma, raw_mask_accuracy_auc_only}`

Why:

* useful if your paper increasingly focuses on ROC AUC rather than thresholded binary classification.

---

## 8. Required YAML behavior

The config system should support:

* fixed **baseline defaults**
* named **study blocks**
* optional per-study overrides
* avoidance of accidental full cross-products across unrelated dimensions

The repo already expects YAML sections such as:

* `paths`
* `datasets`
* `models`
* `retrievers`
* `embeddings`
* `sweeps`
* `runtime`
* `reporting` 

This PRD recommends adding:

* `studies`
* `defaults`
* `overrides`

so you can define **separate ablation batches** cleanly.

---

## 9. YAML output requirements

The YAML should generate the following study groups:

1. `baseline_reproduction`
2. `ablation_model_family`
3. `ablation_mask_count`
4. `ablation_gamma`
5. `ablation_retrieval_depth`
6. `ablation_retrieval_stack`
7. `robustness_cross_dataset`
8. `optional_scale_study`

Each study should:

* fix most parameters,
* vary only one main factor,
* write outputs to a separate results subdirectory.

---

## 10. Success criteria

The YAML config is successful if it:

* runs as multiple **small targeted studies**
* includes **GPT-4o-mini**
* includes **FiQA** and **ArXiv**
* reduces total runs massively compared to a full sweep
* produces cleaner tables and plots for the paper

Target total:

* **core lean plan:** about **40–100 runs**
* **with robustness:** about **100–180 runs**
* **optional scale study:** extra, only if needed

---

# Proposed Lean YAML Configuration

```yaml
paths:
  results_root: results
  cache_root: cache
  datasets_root: data

defaults:
  dataset: healthcaremagic
  model: gpt-4o-mini
  retriever: faiss
  embedding: bge-small-en-v1.5
  mask_count: 10
  gamma: 0.5
  retrieval_k: 5
  seed: 42
  index_size: 500
  eval_members: 100
  eval_non_members: 100
  chunk_size: none
  chunk_overlap: 0
  prompt_variant: strict_format
  proxy_model: gpt2-xl
  mask_policy: proxy_ranked
  faiss_metric: inner_product
  hnsw_ef_search: 64

datasets:
  healthcaremagic:
    enabled: true
    loader: healthcaremagic
    source: default
  msmarco:
    enabled: true
    loader: msmarco
    source: default
  nq:
    enabled: true
    loader: nq
    source: default
  fiqa:
    enabled: true
    loader: fiqa
    source: default
  arxiv:
    enabled: true
    loader: arxiv
    source: default

models:
  gpt-4o-mini:
    provider: openai
    model_name: gpt-4o-mini
    api_mode: chat
    enabled: true
  llama3:
    provider: ollama
    model_name: llama3
    enabled: true
  mistral:
    provider: ollama
    model_name: mistral
    enabled: true
  phi3:
    provider: ollama
    model_name: phi3
    enabled: true

retrievers:
  faiss:
    type: dense
    ann_backend: faiss
    enabled: true
  bm25:
    type: sparse
    enabled: true

embeddings:
  bge-small-en-v1.5:
    provider: huggingface
    model_name: BAAI/bge-small-en-v1.5
    enabled: true
  all-minilm-l6-v2:
    provider: sentence_transformers
    model_name: sentence-transformers/all-MiniLM-L6-v2
    enabled: true

runtime:
  max_parallel_runs: 2
  retry_failed_runs: true
  save_retrieved_docs: true
  save_raw_llm_outputs: true
  deterministic: true

reporting:
  save_jsonl: true
  save_summary_csv: true
  save_markdown_report: true
  save_plots: true
  primary_metric: roc_auc
  secondary_metrics:
    - mask_accuracy
    - f1
    - retrieval_recall

studies:
  baseline_reproduction:
    description: "Single anchored baseline using GPT-4o-mini and HealthcareMagic."
    overrides:
      dataset: healthcaremagic
      model: gpt-4o-mini
      retriever: faiss
      embedding: bge-small-en-v1.5
      mask_count: 10
      gamma: 0.5
      retrieval_k: 5
      seed: 42
    sweep: {}

  ablation_model_family:
    description: "Vary only the LLM family."
    overrides:
      dataset: healthcaremagic
      retriever: faiss
      embedding: bge-small-en-v1.5
      mask_count: 10
      gamma: 0.5
      retrieval_k: 5
    sweep:
      model:
        - gpt-4o-mini
        - llama3
        - mistral
        - phi3

  ablation_mask_count:
    description: "Vary only mask count M."
    overrides:
      dataset: healthcaremagic
      model: gpt-4o-mini
      retriever: faiss
      embedding: bge-small-en-v1.5
      gamma: 0.5
      retrieval_k: 5
    sweep:
      mask_count:
        - 3
        - 5
        - 10
        - 15
        - 20

  ablation_gamma:
    description: "Vary only membership threshold gamma."
    overrides:
      dataset: healthcaremagic
      model: gpt-4o-mini
      retriever: faiss
      embedding: bge-small-en-v1.5
      mask_count: 10
      retrieval_k: 5
    sweep:
      gamma:
        - 0.3
        - 0.5
        - 0.7
        - 0.9

  ablation_retrieval_depth:
    description: "Vary only top-K retrieval depth."
    overrides:
      dataset: healthcaremagic
      model: gpt-4o-mini
      retriever: faiss
      embedding: bge-small-en-v1.5
      mask_count: 10
      gamma: 0.5
    sweep:
      retrieval_k:
        - 1
        - 3
        - 5
        - 10

  ablation_retrieval_stack:
    description: "Vary retriever and embedding with model fixed."
    overrides:
      dataset: healthcaremagic
      model: gpt-4o-mini
      mask_count: 10
      gamma: 0.5
      retrieval_k: 5
    sweep:
      retriever:
        - faiss
        - bm25
      embedding:
        - bge-small-en-v1.5
        - all-minilm-l6-v2

  robustness_cross_dataset:
    description: "Check whether main findings hold across datasets using only top models."
    overrides:
      retriever: faiss
      embedding: bge-small-en-v1.5
      mask_count: 10
      gamma: 0.5
      retrieval_k: 5
    sweep:
      dataset:
        - healthcaremagic
        - msmarco
        - nq
        - fiqa
        - arxiv
      model:
        - gpt-4o-mini
        - llama3

  optional_scale_study:
    description: "Optional study for index-size sensitivity."
    overrides:
      dataset: healthcaremagic
      model: gpt-4o-mini
      retriever: faiss
      embedding: bge-small-en-v1.5
      mask_count: 10
      gamma: 0.5
      retrieval_k: 5
    sweep:
      index_size:
        - 500
        - 2000
        - 10000
      seed:
        - 42
        - 1337
```

---

# Recommended next extensions

## Strongest additions

If you want the best paper upgrade for lowest extra cost, add these first:

1. **GPT-4o-mini**
2. **FiQA**
3. **ArXiv**
4. **`γ` ablation**
5. **index-size sensitivity**
6. **3 seeds for only the strongest studies**

## Nice-to-have additions

After that:

* chunking study
* prompt-format strictness study
* proxy-model study
* mask-policy study

---

# Clean experiment roadmap

## Phase 1 — sanity

Run:

* `baseline_reproduction`

## Phase 2 — core ablation

Run:

* `ablation_model_family`
* `ablation_mask_count`
* `ablation_gamma`
* `ablation_retrieval_depth`

## Phase 3 — robustness

Run:

* `robustness_cross_dataset`

## Phase 4 — optional scale

Run:

* `optional_scale_study`
