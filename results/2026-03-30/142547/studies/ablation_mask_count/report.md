# MBA Experiment Report

## Summary

- Successful runs: `5`
- Failed runs: `0`
- Best study/config: `ablation_mask_count / healthcaremagic / gpt-4o-mini / faiss / M=15 / K=5 / gamma=0.5000`
- Best AUC: `1.0000`
- Best F1: `0.9434`

## Dataset: healthcaremagic

### Model Comparison

| Model | AUC | F1 | Recall |
| --- | --- | --- | --- |
| gpt-4o-mini | 0.9710 | 0.8871 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| faiss | bge-small-en-v1.5 | 0.9710 | 0.8871 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 20 | 5 | 0.5000 | 1 | 0.9259 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 15 | 5 | 0.5000 | 1 | 0.9434 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9930 | 0.8850 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9930 | 0.8850 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 5 | 5 | 0.5000 | 0.9542 | 0.8596 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 3 | 5 | 0.5000 | 0.9076 | 0.8214 |

### M x K Matrix: gpt-4o-mini

| M | 5 |
| --- | --- |
| 3 | 0.9076 |
| 5 | 0.9542 |
| 10 | 0.9930 |
| 15 | 1 |
| 20 | 1 |
