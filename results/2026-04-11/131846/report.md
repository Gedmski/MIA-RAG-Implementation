# MBA Experiment Report

## Summary

- Successful runs: `51`
- Failed runs: `1`
- Best study/config: `ablation_model_scale / healthcaremagic / llama3.1-8b / faiss / M=10 / K=5 / gamma=0.5000`
- Best AUC: `1.0000`
- Best F1: `0.9434`

## Study Overview

| Study | AUC | F1 | Recall |
| --- | --- | --- | --- |
| ablation_model_scale | 0.9981 | 0.8752 | 1 |
| baseline_reproduction | 0.9970 | 0.8850 | 1 |
| ablation_retrieval_depth | 0.9964 | 0.8792 | 1 |
| ablation_retrieval_stack | 0.9946 | 0.8697 | 1 |
| ablation_domain_stack_control | 0.9937 | 0.9062 | 1 |
| ablation_gamma | 0.9936 | 0.8688 | 1 |
| optional_scale_study | 0.9904 | 0.8910 | 1 |
| robustness_cross_dataset | 0.9871 | 0.9048 | 1 |
| ablation_mask_count | 0.9678 | 0.8808 | 1 |
| ablation_model_family | 0.9041 | 0.8316 | 1 |

## Study: ablation_domain_stack_control

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

## Study: ablation_gamma

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

## Study: ablation_mask_count

## Dataset: healthcaremagic

### Model Comparison

| Model | AUC | F1 | Recall |
| --- | --- | --- | --- |
| gpt-4o-mini | 0.9678 | 0.8808 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| faiss | bge-small-en-v1.5 | 0.9678 | 0.8808 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 20 | 5 | 0.5000 | 1 | 0.9174 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 15 | 5 | 0.5000 | 1 | 0.9434 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9932 | 0.8696 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9932 | 0.8696 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 5 | 5 | 0.5000 | 0.9426 | 0.8522 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 3 | 5 | 0.5000 | 0.9032 | 0.8214 |

### M x K Matrix: gpt-4o-mini

| M | 5 |
| --- | --- |
| 3 | 0.9032 |
| 5 | 0.9426 |
| 10 | 0.9932 |
| 15 | 1 |
| 20 | 1 |

## Study: ablation_model_family

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

## Study: ablation_model_scale

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

## Study: ablation_retrieval_depth

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

## Study: ablation_retrieval_stack

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

## Study: baseline_reproduction

## Dataset: healthcaremagic

### Model Comparison

| Model | AUC | F1 | Recall |
| --- | --- | --- | --- |
| gpt-4o-mini | 0.9970 | 0.8850 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| faiss | bge-small-en-v1.5 | 0.9970 | 0.8850 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9970 | 0.8850 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9970 | 0.8850 |

### M x K Matrix: gpt-4o-mini

| M | 5 |
| --- | --- |
| 10 | 0.9970 |

## Study: optional_scale_study

## Dataset: healthcaremagic

### Model Comparison

| Model | AUC | F1 | Recall |
| --- | --- | --- | --- |
| gpt-4o-mini | 0.9904 | 0.8910 | 1 |

### Retriever x Embedding

| Retriever | Embedding | AUC | F1 | Recall |
| --- | --- | --- | --- | --- |
| faiss | bge-small-en-v1.5 | 0.9904 | 0.8910 | 1 |

### Best And Worst Configurations

| llm_model | retriever_type | embedding_model | num_masks | retriever_k | gamma | auc | f1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9978 | 0.8850 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9966 | 0.8772 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9880 | 0.9091 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9966 | 0.8772 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9880 | 0.9091 |
| gpt-4o-mini | faiss | bge-small-en-v1.5 | 10 | 5 | 0.5000 | 0.9790 | 0.8929 |

### M x K Matrix: gpt-4o-mini

| M | 5 |
| --- | --- |
| 10 | 0.9904 |

## Study: robustness_cross_dataset

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
