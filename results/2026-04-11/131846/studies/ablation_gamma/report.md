# MBA Experiment Report

## Summary

- Successful runs: `4`
- Failed runs: `0`
- Best study/config: `ablation_gamma / healthcaremagic / gpt-4o-mini / faiss / M=10 / K=5 / gamma=0.9000`
- Best AUC: `0.9956`
- Best F1: `0.8636`

## Dataset: healthcaremagic

### Model Comparison

| Model | AUC | F1 | Recall |
| --- | --- | --- | --- |
| gpt-4o-mini | 0.9936 | 0.8688 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| faiss | bge-small-en-v1.5 | 0.9936 | 0.8688 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.9000 | 0.9956 | 0.8636 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.3000 | 0.9950 | 0.7634 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9932 | 0.8772 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.3000 | 0.9950 | 0.7634 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9932 | 0.8772 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.7000 | 0.9904 | 0.9709 |

### M x K Matrix: gpt-4o-mini

| M | 5 |
| --- | --- |
| 10 | 0.9936 |
