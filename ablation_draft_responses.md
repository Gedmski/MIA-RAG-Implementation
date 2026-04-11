# Ablation Draft Responses

This memo answers the unresolved draft comments in the MBMIA ablation section. Each item includes a direct answer, a manuscript-ready replacement, and the current evidence status in this repo.

## 1. Mask Accuracy sentence is unclear

**Draft comment**

> Karima: This sentence is unclear.

**Direct answer**

The sentence should define the metric operationally, not interpret it abstractly. The cleanest wording is to say that Mask Accuracy is the fraction of masked slots reconstructed exactly against the answer key for a single target document.

**Manuscript-ready replacement**

Mask Accuracy is the fraction of masked positions whose reconstructed value exactly matches the ground-truth answer key for a given target document. A higher Mask Accuracy means that the generator recovered more of the masked lexical items required by the probe.

**Evidence / status**

- This is a wording fix, not a new empirical claim.
- The implementation now evaluates exact reconstruction explicitly in [src/mia_rag/pipeline.py](D:\GABRIEL\Research\MIA-RAG-Implementation\src\mia_rag\pipeline.py).

## 2. “Generation failure” is unclear

**Draft comment**

> Karima: Generation failure is unclear. Rephrase, please.

**Direct answer**

The term should be defined using the retrieval and reconstruction signals already measured in the pipeline. In this repo, generation failure is now defined as a member example where the target document was retrieved but the reconstruction score still falls below the decision threshold.

**Manuscript-ready replacement**

A retrieval failure occurs when the true member document is absent from the top-K retrieved context. A generation failure occurs when the true member document is retrieved successfully, but the response still does not reconstruct enough masked items to meet the membership criterion; in our implementation, this means `retrieval_hit = 1` and `Mask Accuracy < γ`.

**Evidence / status**

- The definition is now encoded in the new `generation_failure_rate` aggregate in [src/mia_rag/pipeline.py](D:\GABRIEL\Research\MIA-RAG-Implementation\src\mia_rag\pipeline.py).
- Structured summaries now expose this diagnostic through [src/mia_rag/reporting.py](D:\GABRIEL\Research\MIA-RAG-Implementation\src\mia_rag\reporting.py).

## 3. Figure size needs to be larger

**Draft comment**

> Sami: I couldn’t increase or decrease the size of the figure! Can you make it larger.

**Direct answer**

Yes. The reporting layer now exports larger figures with higher DPI and tighter bounding boxes so the ablation plots are easier to use in the paper.

**Manuscript-ready replacement**

Figure 5 uses a higher-resolution export generated directly from the structured study outputs, with an enlarged canvas and higher DPI for manuscript insertion.

**Evidence / status**

- Plot generation has been updated in [src/mia_rag/reporting.py](D:\GABRIEL\Research\MIA-RAG-Implementation\src\mia_rag\reporting.py).
- The intended replacement source for the mask-count figure is the generated plot at `results/<date>/<run_id>/studies/ablation_mask_count/plots/healthcaremagic_gpt-4o-mini_auc_vs_m.png`.
- A fresh run is still required to materialize the larger asset.

## 4. The Llama-versus-GPT explanation needs deeper reasons, and GPT variants should be tried

**Draft comment**

> Karima: This important finding should be further and more deeply explained. Potential reasons? Trying a GPT-based model is also needed as we agreed.

**Direct answer**

The current evidence supports a narrower claim than “Llama is more vulnerable.” In the existing HealthcareMagic family comparison, retrieval recall is uniformly perfect, so the main observable differences are downstream generation behaviors: strict output-format compliance, exact lexical reconstruction, and threshold crossing under exact-match scoring. GPT is already present in the current study through `gpt-4o-mini`; this implementation expands that comparison with a dedicated `ablation_model_scale` study covering `gpt-4o-mini`, `gpt-4o`, `llama3.1:8b`, and `llama3.1:70b`.

**Manuscript-ready replacement**

Because Retrieval Recall is 1.0 for all model-family runs, the observed AUC differences are unlikely to originate from retrieval. A more defensible interpretation is that the attack is most sensitive to generation-side behavior under strict exact-match scoring: some models follow the mask-reconstruction format more consistently, return shorter and less noisy answers, and more often reproduce the exact lexical items required by the answer key. In that setting, stronger attack performance should be read as cleaner exposure of the membership signal under the probe protocol, not as a blanket statement that one model family is universally more vulnerable in every RAG deployment. To sharpen this analysis, we extend the comparison beyond the original GPT-4o-mini baseline with a dedicated scale study that contrasts GPT tiers and Llama parameter scales under the same retrieval setup.

**Evidence / status**

- Current family-comparison evidence is in [results_report.md](D:\GABRIEL\Research\MIA-RAG-Implementation\results_report.md) and [results/2026-03-30/142547/studies/ablation_model_family/summary.csv](D:\GABRIEL\Research\MIA-RAG-Implementation\results\2026-03-30\142547\studies\ablation_model_family\summary.csv).
- The code now aggregates format-coverage and exact-reconstruction diagnostics in [src/mia_rag/pipeline.py](D:\GABRIEL\Research\MIA-RAG-Implementation\src\mia_rag\pipeline.py).
- The expanded GPT/Llama comparison is configured in [configs/lean_ablation.yaml](D:\GABRIEL\Research\MIA-RAG-Implementation\configs\lean_ablation.yaml).
- New empirical evidence still requires rerunning the study because the current environment lacks `OPENAI_API_KEY` and local Ollama models.

## 5. Are the observed dataset effects really domain effects rather than retrieval-stack effects?

**Draft comment**

> Karima: Are you sure that this is due to the dataset domain, not the retriever/embedding factors?

**Direct answer**

Not from the current evidence alone. The existing cross-dataset table fixes the retriever and embedding, which shows that strong performance persists across several domains under one stack, but it does not by itself prove that domain is the dominant factor relative to the retrieval stack. That is why this implementation adds a dedicated `ablation_domain_stack_control` study.

**Manuscript-ready replacement**

The current cross-dataset results show that strong MBA performance is not limited to medical text when the retrieval stack is fixed, but they do not by themselves isolate domain effects from retriever or embedding effects. We therefore add a controlled domain-versus-stack study that fixes the generator and varies dataset, retriever, and embedding jointly. The appropriate conclusion before that control is run is modest: multiple domains appear vulnerable under the baseline stack, but the relative contribution of domain versus retrieval-stack choice must be established by controlled ablation.

**Evidence / status**

- Current cross-dataset evidence is summarized in [results_report.md](D:\GABRIEL\Research\MIA-RAG-Implementation\results_report.md).
- The new control study is defined in [configs/lean_ablation.yaml](D:\GABRIEL\Research\MIA-RAG-Implementation\configs\lean_ablation.yaml).
- Report support for this study has been added in [src/mia_rag/reporting.py](D:\GABRIEL\Research\MIA-RAG-Implementation\src\mia_rag\reporting.py).
- No controlled conclusion should be inserted into the manuscript until that study is rerun.

## 6. GPT comparison is already present, but it is being expanded

**Direct answer**

The manuscript should not imply that GPT was absent from the repo before this change. `gpt-4o-mini` already appears in the baseline and family-comparison studies. What changes here is the scope of the GPT analysis: it is expanded from a single hosted baseline to a dedicated tier comparison.

**Manuscript-ready replacement**

Our implementation already included GPT-4o-mini as the hosted-model reference point. The present revision expands that comparison by adding a dedicated model-scale study rather than introducing GPT for the first time.

**Evidence / status**

- Existing GPT usage appears in [configs/lean_ablation.yaml](D:\GABRIEL\Research\MIA-RAG-Implementation\configs\lean_ablation.yaml) and [results_report.md](D:\GABRIEL\Research\MIA-RAG-Implementation\results_report.md).
