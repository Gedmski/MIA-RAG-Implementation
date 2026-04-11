# MBA Experiment Report

## Summary

- Successful runs: `4`
- Failed runs: `0`
- Best study/config: `ablation_retrieval_stack / healthcaremagic / gpt-4o-mini / faiss / M=10 / K=5 / gamma=0.5000`
- Best AUC: `0.9958`
- Best F1: `0.8621`

## Dataset: healthcaremagic

### Model Comparison

| Model | AUC | F1 | Recall |
| --- | --- | --- | --- |
| gpt-4o-mini | 0.9946 | 0.8697 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| faiss | all-minilm-l6-v2 | 0.9958 | 0.8621 | 1 |
| bm25 | all-minilm-l6-v2 | 0.9950 | 0.8696 | 1 |
| bm25 | bge-small-en-v1.5 | 0.9942 | 0.8621 | 1 |
| faiss | bge-small-en-v1.5 | 0.9932 | 0.8850 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-4o-mini | faiss | all-minilm-l6-v2 | 10 | 5 | 0.5000 | 0.9958 | 0.8621 |
| gpt-4o-mini | bm25 | all-minilm-l6-v2 | 10 | 5 | 0.5000 | 0.9950 | 0.8696 |
| gpt-4o-mini | bm25 | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9942 | 0.8621 |
| gpt-4o-mini | bm25 | all-minilm-l6-v2 | 10 | 5 | 0.5000 | 0.9950 | 0.8696 |
| gpt-4o-mini | bm25 | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9942 | 0.8621 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9932 | 0.8850 |

### M x K Matrix: gpt-4o-mini

| M | 5 |
| --- | --- |
| 10 | 0.9946 |
