# MBA Experiment Report

## Summary

- Successful runs: `4`
- Failed runs: `0`
- Best study/config: `ablation_model_family / healthcaremagic / llama3 / faiss / M=10 / K=5 / gamma=0.5000`
- Best AUC: `0.9980`
- Best F1: `0.9524`

## Dataset: healthcaremagic

### Model Comparison

| Model | AUC | F1 | Recall |
| --- | --- | --- | --- |
| llama3 | 0.9980 | 0.9524 | 1 |
| gpt-4o-mini | 0.9934 | 0.8850 | 1 |
| phi3 | 0.9104 | 0.7179 | 1 |
| mistral | 0.7144 | 0.7711 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| faiss | bge-small-en-v1.5 | 0.9041 | 0.8316 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| llama3 | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9980 | 0.9524 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9934 | 0.8850 |
| phi3 | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9104 | 0.7179 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9934 | 0.8850 |
| phi3 | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9104 | 0.7179 |
| mistral | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.7144 | 0.7711 |

### M x K Matrix: gpt-4o-mini

| M | 5 |
| --- | --- |
| 10 | 0.9934 |

### M x K Matrix: llama3

| M | 5 |
| --- | --- |
| 10 | 0.9980 |

### M x K Matrix: mistral

| M | 5 |
| --- | --- |
| 10 | 0.7144 |

### M x K Matrix: phi3

| M | 5 |
| --- | --- |
| 10 | 0.9104 |
