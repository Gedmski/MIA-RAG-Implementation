# MBA Experiment Report

## Summary

- Successful runs: `10`
- Failed runs: `0`
- Best study/config: `robustness_cross_dataset / fiqa / gpt-4o-mini / faiss / M=10 / K=5 / gamma=0.5000`
- Best AUC: `0.9992`
- Best F1: `0.9091`

## Dataset: arxiv

### Model Comparison

| Model | AUC | F1 | Recall |
| --- | --- | --- | --- |
| llama3 | 0.9936 | 0.9709 | 1 |
| gpt-4o-mini | 0.9890 | 0.9346 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| faiss | bge-small-en-v1.5 | 0.9913 | 0.9527 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| llama3 | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9936 | 0.9709 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9890 | 0.9346 |
| llama3 | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9936 | 0.9709 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9890 | 0.9346 |

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
| gpt-4o-mini | 0.9992 | 0.9091 | 1 |
| llama3 | 0.9826 | 0.9796 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| faiss | bge-small-en-v1.5 | 0.9909 | 0.9443 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9992 | 0.9091 |
| llama3 | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9826 | 0.9796 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9992 | 0.9091 |
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
| gpt-4o-mini | 0.9984 | 0.8850 | 1 |
| llama3 | 0.9980 | 0.9524 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| faiss | bge-small-en-v1.5 | 0.9982 | 0.9187 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9984 | 0.8850 |
| llama3 | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9980 | 0.9524 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9984 | 0.8850 |
| llama3 | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9980 | 0.9524 |

### M x K Matrix: gpt-4o-mini

| M | 5 |
| --- | --- |
| 10 | 0.9984 |

### M x K Matrix: llama3

| M | 5 |
| --- | --- |
| 10 | 0.9980 |

## Dataset: msmarco

### Model Comparison

| Model | AUC | F1 | Recall |
| --- | --- | --- | --- |
| gpt-4o-mini | 0.9740 | 0.7812 | 1 |
| llama3 | 0.9652 | 0.8772 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| faiss | bge-small-en-v1.5 | 0.9696 | 0.8292 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9740 | 0.7812 |
| llama3 | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9652 | 0.8772 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9740 | 0.7812 |
| llama3 | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9652 | 0.8772 |

### M x K Matrix: gpt-4o-mini

| M | 5 |
| --- | --- |
| 10 | 0.9740 |

### M x K Matrix: llama3

| M | 5 |
| --- | --- |
| 10 | 0.9652 |

## Dataset: nq

### Model Comparison

| Model | AUC | F1 | Recall |
| --- | --- | --- | --- |
| llama3 | 0.9916 | 0.9515 | 1 |
| gpt-4o-mini | 0.9798 | 0.8065 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| faiss | bge-small-en-v1.5 | 0.9857 | 0.8790 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| llama3 | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9916 | 0.9515 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9798 | 0.8065 |
| llama3 | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9916 | 0.9515 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9798 | 0.8065 |

### M x K Matrix: gpt-4o-mini

| M | 5 |
| --- | --- |
| 10 | 0.9798 |

### M x K Matrix: llama3

| M | 5 |
| --- | --- |
| 10 | 0.9916 |
