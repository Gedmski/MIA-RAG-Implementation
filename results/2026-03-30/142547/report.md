# MBA Experiment Report

## Summary

- Successful runs: `36`
- Failed runs: `0`
- Best study/config: `ablation_mask_count / healthcaremagic / gpt-4o-mini / faiss / M=15 / K=5 / gamma=0.5000`
- Best AUC: `1.0000`
- Best F1: `0.9434`

## Study Overview

| Study | AUC | F1 | Recall |
| --- | --- | --- | --- |
| ablation_retrieval_depth | 0.9968 | 0.8793 | 1 |
| ablation_gamma | 0.9967 | 0.8734 | 1 |
| ablation_retrieval_stack | 0.9947 | 0.8715 | 1 |
| baseline_reproduction | 0.9940 | 0.8850 | 1 |
| optional_scale_study | 0.9905 | 0.8933 | 1 |
| robustness_cross_dataset | 0.9884 | 0.9036 | 1 |
| ablation_mask_count | 0.9710 | 0.8871 | 1 |
| ablation_model_family | 0.9088 | 0.8318 | 1 |

## Study: ablation_gamma

## Dataset: healthcaremagic

### Model Comparison

| Model | AUC | F1 | Recall |
| --- | --- | --- | --- |
| gpt-4o-mini | 0.9967 | 0.8734 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| faiss | bge-small-en-v1.5 | 0.9967 | 0.8734 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.9000 | 0.9976 | 0.8764 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9966 | 0.8850 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.7000 | 0.9964 | 0.9804 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9966 | 0.8850 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.7000 | 0.9964 | 0.9804 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.3000 | 0.9962 | 0.7519 |

### M x K Matrix: gpt-4o-mini

| M | 5 |
| --- | --- |
| 10 | 0.9967 |

## Study: ablation_mask_count

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

## Study: ablation_model_family

## Dataset: healthcaremagic

### Model Comparison

| Model | AUC | F1 | Recall |
| --- | --- | --- | --- |
| llama3 | 0.9980 | 0.9524 | 1 |
| gpt-4o-mini | 0.9962 | 0.8696 | 1 |
| phi3 | 0.9266 | 0.7342 | 1 |
| mistral | 0.7144 | 0.7711 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| faiss | bge-small-en-v1.5 | 0.9088 | 0.8318 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| llama3 | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9980 | 0.9524 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9962 | 0.8696 |
| phi3 | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9266 | 0.7342 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9962 | 0.8696 |
| phi3 | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9266 | 0.7342 |
| mistral | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.7144 | 0.7711 |

### M x K Matrix: gpt-4o-mini

| M | 5 |
| --- | --- |
| 10 | 0.9962 |

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
| 10 | 0.9266 |

## Study: ablation_retrieval_depth

## Dataset: healthcaremagic

### Model Comparison

| Model | AUC | F1 | Recall |
| --- | --- | --- | --- |
| gpt-4o-mini | 0.9968 | 0.8793 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| faiss | bge-small-en-v1.5 | 0.9968 | 0.8793 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 1 | 0.5000 | 1 | 0.8929 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9984 | 0.8772 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 3 | 0.5000 | 0.9960 | 0.8850 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9984 | 0.8772 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 3 | 0.5000 | 0.9960 | 0.8850 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 10 | 0.5000 | 0.9928 | 0.8621 |

### M x K Matrix: gpt-4o-mini

| M | 1 | 3 | 5 | 10 |
| --- | --- | --- | --- | --- |
| 10 | 1 | 0.9960 | 0.9984 | 0.9928 |

## Study: ablation_retrieval_stack

## Dataset: healthcaremagic

### Model Comparison

| Model | AUC | F1 | Recall |
| --- | --- | --- | --- |
| gpt-4o-mini | 0.9947 | 0.8715 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| faiss | bge-small-en-v1.5 | 0.9954 | 0.8850 | 1 |
| bm25 | bge-small-en-v1.5 | 0.9950 | 0.8696 | 1 |
| faiss | all-minilm-l6-v2 | 0.9946 | 0.8621 | 1 |
| bm25 | all-minilm-l6-v2 | 0.9938 | 0.8696 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9954 | 0.8850 |
| gpt-4o-mini | bm25 | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9950 | 0.8696 |
| gpt-4o-mini | faiss | all-minilm-l6-v2 | 10 | 5 | 0.5000 | 0.9946 | 0.8621 |
| gpt-4o-mini | bm25 | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9950 | 0.8696 |
| gpt-4o-mini | faiss | all-minilm-l6-v2 | 10 | 5 | 0.5000 | 0.9946 | 0.8621 |
| gpt-4o-mini | bm25 | all-minilm-l6-v2 | 10 | 5 | 0.5000 | 0.9938 | 0.8696 |

### M x K Matrix: gpt-4o-mini

| M | 5 |
| --- | --- |
| 10 | 0.9947 |

## Study: baseline_reproduction

## Dataset: healthcaremagic

### Model Comparison

| Model | AUC | F1 | Recall |
| --- | --- | --- | --- |
| gpt-4o-mini | 0.9940 | 0.8850 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| faiss | bge-small-en-v1.5 | 0.9940 | 0.8850 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9940 | 0.8850 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9940 | 0.8850 |

### M x K Matrix: gpt-4o-mini

| M | 5 |
| --- | --- |
| 10 | 0.9940 |

## Study: optional_scale_study

## Dataset: healthcaremagic

### Model Comparison

| Model | AUC | F1 | Recall |
| --- | --- | --- | --- |
| gpt-4o-mini | 0.9905 | 0.8933 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| faiss | bge-small-en-v1.5 | 0.9905 | 0.8933 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9968 | 0.8929 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9962 | 0.8696 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9888 | 0.9259 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9962 | 0.8696 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9888 | 0.9259 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9802 | 0.8850 |

### M x K Matrix: gpt-4o-mini

| M | 5 |
| --- | --- |
| 10 | 0.9905 |

## Study: robustness_cross_dataset

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
