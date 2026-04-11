# MBA Experiment Report

## Summary

- Successful runs: `11`
- Failed runs: `1`
- Best study/config: `ablation_domain_stack_control / fiqa / gpt-4o-mini / faiss / M=10 / K=5 / gamma=0.5000`
- Best AUC: `0.9992`
- Best F1: `0.9009`

## Dataset: arxiv

### Model Comparison

| Model | AUC | F1 | Recall |
| --- | --- | --- | --- |
| gpt-4o-mini | 0.9889 | 0.9368 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| faiss | bge-small-en-v1.5 | 0.9890 | 0.9346 | 1 |
| bm25 | bge-small-en-v1.5 | 0.9890 | 0.9434 | 1 |
| bm25 | all-minilm-l6-v2 | 0.9888 | 0.9346 | 1 |
| faiss | all-minilm-l6-v2 | 0.9886 | 0.9346 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9890 | 0.9346 |
| gpt-4o-mini | bm25 | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9890 | 0.9434 |
| gpt-4o-mini | bm25 | all-minilm-l6-v2 | 10 | 5 | 0.5000 | 0.9888 | 0.9346 |
| gpt-4o-mini | bm25 | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9890 | 0.9434 |
| gpt-4o-mini | bm25 | all-minilm-l6-v2 | 10 | 5 | 0.5000 | 0.9888 | 0.9346 |
| gpt-4o-mini | faiss | all-minilm-l6-v2 | 10 | 5 | 0.5000 | 0.9886 | 0.9346 |

### M x K Matrix: gpt-4o-mini

| M | 5 |
| --- | --- |
| 10 | 0.9889 |

## Dataset: fiqa

### Model Comparison

| Model | AUC | F1 | Recall |
| --- | --- | --- | --- |
| gpt-4o-mini | 0.9978 | 0.9030 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| faiss | all-minilm-l6-v2 | 0.9992 | 0.9009 | 1 |
| bm25 | bge-small-en-v1.5 | 0.9990 | 0.8929 | 1 |
| faiss | bge-small-en-v1.5 | 0.9966 | 0.9174 | 1 |
| bm25 | all-minilm-l6-v2 | 0.9964 | 0.9009 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-4o-mini | faiss | all-minilm-l6-v2 | 10 | 5 | 0.5000 | 0.9992 | 0.9009 |
| gpt-4o-mini | bm25 | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9990 | 0.8929 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9966 | 0.9174 |
| gpt-4o-mini | bm25 | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9990 | 0.8929 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9966 | 0.9174 |
| gpt-4o-mini | bm25 | all-minilm-l6-v2 | 10 | 5 | 0.5000 | 0.9964 | 0.9009 |

### M x K Matrix: gpt-4o-mini

| M | 5 |
| --- | --- |
| 10 | 0.9978 |

## Dataset: healthcaremagic

### Model Comparison

| Model | AUC | F1 | Recall |
| --- | --- | --- | --- |
| gpt-4o-mini | 0.9946 | 0.8696 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| bm25 | all-minilm-l6-v2 | 0.9950 | 0.8621 | 1 |
| bm25 | bge-small-en-v1.5 | 0.9948 | 0.8696 | 1 |
| faiss | bge-small-en-v1.5 | 0.9940 | 0.8772 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-4o-mini | bm25 | all-minilm-l6-v2 | 10 | 5 | 0.5000 | 0.9950 | 0.8621 |
| gpt-4o-mini | bm25 | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9948 | 0.8696 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9940 | 0.8772 |
| gpt-4o-mini | bm25 | all-minilm-l6-v2 | 10 | 5 | 0.5000 | 0.9950 | 0.8621 |
| gpt-4o-mini | bm25 | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9948 | 0.8696 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9940 | 0.8772 |

### M x K Matrix: gpt-4o-mini

| M | 5 |
| --- | --- |
| 10 | 0.9946 |

### Domain vs Retrieval Stack Control

#### Within-Dataset Stack Variance

| Dataset | Mean AUC | Min AUC | Max AUC | Mean F1 | Min F1 | Max F1 | AUC Range |
| --- | --- | --- | --- | --- | --- | --- | --- |
| arxiv | 0.9889 | 0.9886 | 0.9890 | 0.9368 | 0.9346 | 0.9434 | 0.0004 |
| fiqa | 0.9978 | 0.9964 | 0.9992 | 0.9030 | 0.8929 | 0.9174 | 0.0028 |
| healthcaremagic | 0.9946 | 0.9940 | 0.9950 | 0.8696 | 0.8621 | 0.8772 | 0.0010 |

#### Cross-Dataset Stack Means

| Retriever | Embedding | Mean AUC | Mean F1 | Mean Recall |
| --- | --- | --- | --- | --- |
| bm25 | bge-small-en-v1.5 | 0.9943 | 0.9019 | 1 |
| faiss | all-minilm-l6-v2 | 0.9939 | 0.9177 | 1 |
| bm25 | all-minilm-l6-v2 | 0.9934 | 0.8992 | 1 |
| faiss | bge-small-en-v1.5 | 0.9932 | 0.9097 | 1 |
