# MBA Experiment Report

## Summary

- Successful runs: `4`
- Failed runs: `0`
- Best study/config: `ablation_model_scale / healthcaremagic / llama3.1-8b / faiss / M=10 / K=5 / gamma=0.5000`
- Best AUC: `1.0000`
- Best F1: `0.9434`

## Dataset: healthcaremagic

### Model Comparison

| Model | AUC | F1 | Recall |
| --- | --- | --- | --- |
| llama3.1-8b | 1 | 0.9434 | 1 |
| llama3.1-70b | 0.9994 | 0.8929 | 1 |
| gpt-4o | 0.9980 | 0.7874 | 1 |
| gpt-4o-mini | 0.9950 | 0.8772 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| faiss | bge-small-en-v1.5 | 0.9981 | 0.8752 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| llama3.1-8b | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 1 | 0.9434 |
| llama3.1-70b | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9994 | 0.8929 |
| gpt-4o | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9980 | 0.7874 |
| llama3.1-70b | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9994 | 0.8929 |
| gpt-4o | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9980 | 0.7874 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9950 | 0.8772 |

### M x K Matrix: gpt-4o

| M | 5 |
| --- | --- |
| 10 | 0.9980 |

### M x K Matrix: gpt-4o-mini

| M | 5 |
| --- | --- |
| 10 | 0.9950 |

### M x K Matrix: llama3.1-70b

| M | 5 |
| --- | --- |
| 10 | 0.9994 |

### M x K Matrix: llama3.1-8b

| M | 5 |
| --- | --- |
| 10 | 1 |
