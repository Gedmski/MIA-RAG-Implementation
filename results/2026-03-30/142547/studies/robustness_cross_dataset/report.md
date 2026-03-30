# MBA Experiment Report

## Summary

- Successful runs: `10`
- Failed runs: `0`
- Best study/config: `robustness_cross_dataset / fiqa / gpt-4o-mini / faiss / M=10 / K=5 / gamma=0.5000`
- Best AUC: `0.9992`
- Best F1: `0.9009`

## Dataset: arxiv

### Model Comparison

| Model | AUC | F1 | Recall |
| --- | --- | --- | --- |
| llama3 | 0.9936 | 0.9709 | 1 |
| gpt-4o-mini | 0.9890 | 0.9434 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| faiss | bge-small-en-v1.5 | 0.9913 | 0.9571 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| llama3 | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9936 | 0.9709 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9890 | 0.9434 |
| llama3 | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9936 | 0.9709 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9890 | 0.9434 |

### M x K Matrix: gpt-4o-mini

| M | 5 |
| --- | --- |
| 10 | 0.9890 |

### M x K Matrix: llama3

| M | 5 |
| --- | --- |
| 10 | 0.9936 |

## Dataset: fiqa

### Model Comparison

| Model | AUC | F1 | Recall |
| --- | --- | --- | --- |
| gpt-4o-mini | 0.9992 | 0.9009 | 1 |
| llama3 | 0.9826 | 0.9796 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| faiss | bge-small-en-v1.5 | 0.9909 | 0.9402 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9992 | 0.9009 |
| llama3 | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9826 | 0.9796 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9992 | 0.9009 |
| llama3 | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9826 | 0.9796 |

### M x K Matrix: gpt-4o-mini

| M | 5 |
| --- | --- |
| 10 | 0.9992 |

### M x K Matrix: llama3

| M | 5 |
| --- | --- |
| 10 | 0.9826 |

## Dataset: healthcaremagic

### Model Comparison

| Model | AUC | F1 | Recall |
| --- | --- | --- | --- |
| llama3 | 0.9980 | 0.9524 | 1 |
| gpt-4o-mini | 0.9966 | 0.8850 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| faiss | bge-small-en-v1.5 | 0.9973 | 0.9187 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| llama3 | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9980 | 0.9524 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9966 | 0.8850 |
| llama3 | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9980 | 0.9524 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9966 | 0.8850 |

### M x K Matrix: gpt-4o-mini

| M | 5 |
| --- | --- |
| 10 | 0.9966 |

### M x K Matrix: llama3

| M | 5 |
| --- | --- |
| 10 | 0.9980 |

## Dataset: msmarco

### Model Comparison

| Model | AUC | F1 | Recall |
| --- | --- | --- | --- |
| gpt-4o-mini | 0.9838 | 0.7874 | 1 |
| llama3 | 0.9652 | 0.8772 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| faiss | bge-small-en-v1.5 | 0.9745 | 0.8323 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9838 | 0.7874 |
| llama3 | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9652 | 0.8772 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9838 | 0.7874 |
| llama3 | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9652 | 0.8772 |

### M x K Matrix: gpt-4o-mini

| M | 5 |
| --- | --- |
| 10 | 0.9838 |

### M x K Matrix: llama3

| M | 5 |
| --- | --- |
| 10 | 0.9652 |

## Dataset: nq

### Model Comparison

| Model | AUC | F1 | Recall |
| --- | --- | --- | --- |
| llama3 | 0.9916 | 0.9515 | 1 |
| gpt-4o-mini | 0.9848 | 0.7874 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| faiss | bge-small-en-v1.5 | 0.9882 | 0.8694 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| llama3 | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9916 | 0.9515 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9848 | 0.7874 |
| llama3 | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9916 | 0.9515 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9848 | 0.7874 |

### M x K Matrix: gpt-4o-mini

| M | 5 |
| --- | --- |
| 10 | 0.9848 |

### M x K Matrix: llama3

| M | 5 |
| --- | --- |
| 10 | 0.9916 |
