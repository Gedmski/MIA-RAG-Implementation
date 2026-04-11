# MBA Experiment Report

## Summary

- Successful runs: `4`
- Failed runs: `0`
- Best study/config: `ablation_retrieval_depth / healthcaremagic / gpt-4o-mini / faiss / M=10 / K=1 / gamma=0.5000`
- Best AUC: `0.9992`
- Best F1: `0.8850`

## Dataset: healthcaremagic

### Model Comparison

| Model | AUC | F1 | Recall |
| --- | --- | --- | --- |
| gpt-4o-mini | 0.9964 | 0.8792 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| faiss | bge-small-en-v1.5 | 0.9964 | 0.8792 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 1 | 0.5000 | 0.9992 | 0.8850 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9970 | 0.8772 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 3 | 0.5000 | 0.9956 | 0.8850 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9970 | 0.8772 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 3 | 0.5000 | 0.9956 | 0.8850 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 10 | 0.5000 | 0.9938 | 0.8696 |

### M x K Matrix: gpt-4o-mini

| M | 1 | 3 | 5 | 10 |
| --- | --- | --- | --- | --- |
| 10 | 0.9992 | 0.9956 | 0.9970 | 0.9938 |
