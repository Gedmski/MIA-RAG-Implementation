# Experiment Results Analysis

## 1. Overall Best Performance

The highest AUC achieving configuration was:
- **LLM**: `llama3`
- **Embedding**: `BAAI/bge-small-en-v1.5`
- **Retriever**: `faiss`
- **Dataset**: `healthcaremagic`
- **Num Masks**: `10`
- **Retriever K**: `5`
- **AUC**: **0.9994**

## 2. Performance by LLM

| LLM | AUC | Retrieval Recall |
| --- | --- | --- |
| llama3 | 0.9788 | 1.0000 |
| mistral | 0.8421 | 1.0000 |
| phi3 | 0.5293 | 1.0000 |

## 3. Performance by Embedding Model

| Embedding | AUC | Retrieval Recall |
| --- | --- | --- |
| sentence-transformers/all-MiniLM-L6-v2 | 0.7926 | 1.0000 |
| BAAI/bge-small-en-v1.5 | 0.7743 | 1.0000 |

## 4. Performance by Retriever

| Retriever | AUC | Retrieval Recall |
| --- | --- | --- |
| faiss | 0.7906 | 1.0000 |
| bm25 | 0.7763 | 1.0000 |

## 5. Dataset Difficulty (Average AUC)

| Dataset | AUC | Retrieval Recall |
| --- | --- | --- |
| healthcaremagic | 0.7555 | 1.0000 |
| msmarco | 0.7874 | 1.0000 |
| nq | 0.8074 | 1.0000 |

## 6. Performance by Num Masks

| Num Masks | AUC | Retrieval Recall |
| --- | --- | --- |
| 5.0000 | 0.8019 | 1.0000 |
| 10.0000 | 0.7826 | 1.0000 |
| 15.0000 | 0.7657 | 1.0000 |

## 7. Performance by Retriever K

| Retriever K | AUC | Retrieval Recall |
| --- | --- | --- |
| 3.0000 | 0.7919 | 1.0000 |
| 5.0000 | 0.7750 | 1.0000 |

## 8. All Experiment Runs

| Timestamp | LLM | Embedding | Dataset | Retriever | Num Masks | Retriever K | AUC | Retrieval Recall |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-02-23 22:02:51.357136 | llama3 | BAAI/bge-small-en-v1.5 | healthcaremagic | faiss | 10 | 5 | 0.9994 | 1.0000 |
| 2026-02-24 17:55:14.799731 | llama3 | BAAI/bge-small-en-v1.5 | nq | bm25 | 15 | 5 | 0.9976 | 1.0000 |
| 2026-02-24 16:23:36.830165 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | nq | bm25 | 15 | 5 | 0.9976 | 1.0000 |
| 2026-02-23 20:47:24.942693 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | faiss | 15 | 5 | 0.9974 | 1.0000 |
| 2026-02-23 22:50:04.308995 | llama3 | BAAI/bge-small-en-v1.5 | healthcaremagic | bm25 | 10 | 5 | 0.9964 | 1.0000 |
| 2026-02-23 20:28:49.802448 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | faiss | 10 | 5 | 0.9964 | 1.0000 |
| 2026-02-23 21:15:37.203765 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | bm25 | 10 | 5 | 0.9964 | 1.0000 |
| 2026-02-23 21:55:05.417655 | llama3 | BAAI/bge-small-en-v1.5 | healthcaremagic | faiss | 10 | 3 | 0.9962 | 1.0000 |
| 2026-02-23 22:21:26.509148 | llama3 | BAAI/bge-small-en-v1.5 | healthcaremagic | faiss | 15 | 5 | 0.9962 | 1.0000 |
| 2026-02-23 20:21:00.611009 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | faiss | 10 | 3 | 0.9958 | 1.0000 |
| 2026-02-24 15:29:50.338173 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | nq | faiss | 15 | 3 | 0.9954 | 1.0000 |
| 2026-02-23 21:34:07.541271 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | bm25 | 15 | 5 | 0.9950 | 1.0000 |
| 2026-02-23 23:08:42.495831 | llama3 | BAAI/bge-small-en-v1.5 | healthcaremagic | bm25 | 15 | 5 | 0.9950 | 1.0000 |
| 2026-02-23 20:37:05.178688 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | faiss | 15 | 3 | 0.9948 | 1.0000 |
| 2026-02-23 22:42:27.994180 | llama3 | BAAI/bge-small-en-v1.5 | healthcaremagic | bm25 | 10 | 3 | 0.9940 | 1.0000 |
| 2026-02-23 21:08:01.653887 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | bm25 | 10 | 3 | 0.9940 | 1.0000 |
| 2026-02-24 17:45:21.950349 | llama3 | BAAI/bge-small-en-v1.5 | nq | bm25 | 15 | 3 | 0.9940 | 1.0000 |
| 2026-02-24 16:13:46.636374 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | nq | bm25 | 15 | 3 | 0.9940 | 1.0000 |
| 2026-02-23 21:23:45.416342 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | bm25 | 15 | 3 | 0.9926 | 1.0000 |
| 2026-02-23 22:58:14.075911 | llama3 | BAAI/bge-small-en-v1.5 | healthcaremagic | bm25 | 15 | 3 | 0.9926 | 1.0000 |
| 2026-02-24 16:51:56.617364 | llama3 | BAAI/bge-small-en-v1.5 | nq | faiss | 10 | 5 | 0.9916 | 1.0000 |
| 2026-02-24 17:00:24.306827 | llama3 | BAAI/bge-small-en-v1.5 | nq | faiss | 15 | 3 | 0.9916 | 1.0000 |
| 2026-02-23 21:49:48.970032 | llama3 | BAAI/bge-small-en-v1.5 | healthcaremagic | faiss | 5 | 5 | 0.9916 | 1.0000 |
| 2026-02-24 06:48:47.113158 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | faiss | 10 | 3 | 0.9910 | 1.0000 |
| 2026-02-24 17:30:58.300758 | llama3 | BAAI/bge-small-en-v1.5 | nq | bm25 | 10 | 3 | 0.9908 | 1.0000 |
| 2026-02-23 22:11:00.252913 | llama3 | BAAI/bge-small-en-v1.5 | healthcaremagic | faiss | 15 | 3 | 0.9908 | 1.0000 |
| 2026-02-24 15:59:23.081290 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | nq | bm25 | 10 | 3 | 0.9908 | 1.0000 |
| 2026-02-24 08:06:59.185636 | llama3 | BAAI/bge-small-en-v1.5 | msmarco | faiss | 10 | 3 | 0.9898 | 1.0000 |
| 2026-02-23 20:15:45.195676 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | faiss | 5 | 5 | 0.9898 | 1.0000 |
| 2026-02-24 16:44:02.970887 | llama3 | BAAI/bge-small-en-v1.5 | nq | faiss | 10 | 3 | 0.9886 | 1.0000 |
| 2026-02-24 08:13:31.326094 | llama3 | BAAI/bge-small-en-v1.5 | msmarco | faiss | 10 | 5 | 0.9878 | 1.0000 |
| 2026-02-24 17:11:12.211851 | llama3 | BAAI/bge-small-en-v1.5 | nq | faiss | 15 | 5 | 0.9866 | 1.0000 |
| 2026-02-24 15:14:55.012327 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | nq | faiss | 10 | 3 | 0.9856 | 1.0000 |
| 2026-02-24 07:34:27.997324 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | bm25 | 10 | 5 | 0.9850 | 1.0000 |
| 2026-02-24 08:52:40.041298 | llama3 | BAAI/bge-small-en-v1.5 | msmarco | bm25 | 10 | 5 | 0.9850 | 1.0000 |
| 2026-02-24 16:06:25.876868 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | nq | bm25 | 10 | 5 | 0.9840 | 1.0000 |
| 2026-02-24 17:38:01.168580 | llama3 | BAAI/bge-small-en-v1.5 | nq | bm25 | 10 | 5 | 0.9840 | 1.0000 |
| 2026-02-24 08:46:14.513887 | llama3 | BAAI/bge-small-en-v1.5 | msmarco | bm25 | 10 | 3 | 0.9834 | 1.0000 |
| 2026-02-24 07:27:58.239122 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | bm25 | 10 | 3 | 0.9834 | 1.0000 |
| 2026-02-24 07:02:02.408846 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | faiss | 15 | 3 | 0.9804 | 1.0000 |
| 2026-02-24 06:55:17.885480 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | faiss | 10 | 5 | 0.9792 | 1.0000 |
| 2026-02-23 21:02:53.732261 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | bm25 | 5 | 5 | 0.9790 | 1.0000 |
| 2026-02-23 22:37:19.464461 | llama3 | BAAI/bge-small-en-v1.5 | healthcaremagic | bm25 | 5 | 5 | 0.9790 | 1.0000 |
| 2026-02-24 15:39:56.809199 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | nq | faiss | 15 | 5 | 0.9782 | 1.0000 |
| 2026-02-24 07:11:01.158899 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | faiss | 15 | 5 | 0.9774 | 1.0000 |
| 2026-02-24 15:10:07.183604 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | nq | faiss | 5 | 5 | 0.9770 | 1.0000 |
| 2026-02-24 08:20:16.409899 | llama3 | BAAI/bge-small-en-v1.5 | msmarco | faiss | 15 | 3 | 0.9766 | 1.0000 |
| 2026-02-24 07:40:58.903675 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | bm25 | 15 | 3 | 0.9764 | 1.0000 |
| 2026-02-24 08:59:14.159438 | llama3 | BAAI/bge-small-en-v1.5 | msmarco | bm25 | 15 | 3 | 0.9764 | 1.0000 |
| 2026-02-24 15:22:13.971813 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | nq | faiss | 10 | 5 | 0.9748 | 1.0000 |
| 2026-02-24 08:29:11.814401 | llama3 | BAAI/bge-small-en-v1.5 | msmarco | faiss | 15 | 5 | 0.9744 | 1.0000 |
| 2026-02-24 09:08:00.865248 | llama3 | BAAI/bge-small-en-v1.5 | msmarco | bm25 | 15 | 5 | 0.9738 | 1.0000 |
| 2026-02-24 07:49:45.828747 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | bm25 | 15 | 5 | 0.9738 | 1.0000 |
| 2026-02-24 16:33:57.181840 | llama3 | BAAI/bge-small-en-v1.5 | nq | faiss | 5 | 3 | 0.9676 | 1.0000 |
| 2026-02-24 15:50:14.308432 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | nq | bm25 | 5 | 3 | 0.9666 | 1.0000 |
| 2026-02-24 17:21:48.928720 | llama3 | BAAI/bge-small-en-v1.5 | nq | bm25 | 5 | 3 | 0.9666 | 1.0000 |
| 2026-02-24 17:26:18.253603 | llama3 | BAAI/bge-small-en-v1.5 | nq | bm25 | 5 | 5 | 0.9660 | 1.0000 |
| 2026-02-24 15:54:43.637029 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | nq | bm25 | 5 | 5 | 0.9660 | 1.0000 |
| 2026-02-24 15:05:28.447657 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | nq | faiss | 5 | 3 | 0.9658 | 1.0000 |
| 2026-02-24 16:38:48.342483 | llama3 | BAAI/bge-small-en-v1.5 | nq | faiss | 5 | 5 | 0.9632 | 1.0000 |
| 2026-02-24 02:36:56.500409 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | faiss | 5 | 3 | 0.9600 | 1.0000 |
| 2026-02-23 21:44:48.742374 | llama3 | BAAI/bge-small-en-v1.5 | healthcaremagic | faiss | 5 | 3 | 0.9572 | 1.0000 |
| 2026-02-23 20:58:04.692547 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | bm25 | 5 | 3 | 0.9554 | 1.0000 |
| 2026-02-23 22:32:27.949758 | llama3 | BAAI/bge-small-en-v1.5 | healthcaremagic | bm25 | 5 | 3 | 0.9554 | 1.0000 |
| 2026-02-23 20:10:28.507740 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | faiss | 5 | 3 | 0.9520 | 1.0000 |
| 2026-02-24 18:31:25.723225 | mistral | sentence-transformers/all-MiniLM-L6-v2 | nq | faiss | 15 | 3 | 0.9506 | 1.0000 |
| 2026-02-24 19:33:19.727610 | mistral | sentence-transformers/all-MiniLM-L6-v2 | nq | bm25 | 15 | 3 | 0.9498 | 1.0000 |
| 2026-02-24 21:23:40.266921 | mistral | BAAI/bge-small-en-v1.5 | nq | bm25 | 15 | 3 | 0.9498 | 1.0000 |
| 2026-02-24 06:44:44.283491 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | faiss | 5 | 5 | 0.9486 | 1.0000 |
| 2026-02-24 06:40:33.078971 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | faiss | 5 | 3 | 0.9454 | 1.0000 |
| 2026-02-24 08:42:14.642568 | llama3 | BAAI/bge-small-en-v1.5 | msmarco | bm25 | 5 | 5 | 0.9448 | 1.0000 |
| 2026-02-24 07:23:59.233784 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | bm25 | 5 | 5 | 0.9448 | 1.0000 |
| 2026-02-24 18:14:52.932356 | mistral | sentence-transformers/all-MiniLM-L6-v2 | nq | faiss | 10 | 3 | 0.9432 | 1.0000 |
| 2026-02-24 08:02:49.742744 | llama3 | BAAI/bge-small-en-v1.5 | msmarco | faiss | 5 | 5 | 0.9426 | 1.0000 |
| 2026-02-24 07:58:40.938771 | llama3 | BAAI/bge-small-en-v1.5 | msmarco | faiss | 5 | 3 | 0.9422 | 1.0000 |
| 2026-02-24 01:47:29.357084 | mistral | BAAI/bge-small-en-v1.5 | healthcaremagic | bm25 | 5 | 3 | 0.9394 | 1.0000 |
| 2026-02-24 00:09:02.929310 | mistral | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | bm25 | 5 | 3 | 0.9394 | 1.0000 |
| 2026-02-24 08:38:15.133104 | llama3 | BAAI/bge-small-en-v1.5 | msmarco | bm25 | 5 | 3 | 0.9336 | 1.0000 |
| 2026-02-24 07:19:59.471162 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | bm25 | 5 | 3 | 0.9336 | 1.0000 |
| 2026-02-24 20:05:30.787119 | mistral | BAAI/bge-small-en-v1.5 | nq | faiss | 10 | 3 | 0.9278 | 1.0000 |
| 2026-02-24 19:17:26.111853 | mistral | sentence-transformers/all-MiniLM-L6-v2 | nq | bm25 | 10 | 3 | 0.9276 | 1.0000 |
| 2026-02-24 21:07:45.829901 | mistral | BAAI/bge-small-en-v1.5 | nq | bm25 | 10 | 3 | 0.9276 | 1.0000 |
| 2026-02-24 21:56:38.548859 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | nq | faiss | 10 | 3 | 0.9264 | 1.0000 |
| 2026-02-24 11:00:10.814928 | mistral | BAAI/bge-small-en-v1.5 | msmarco | faiss | 15 | 3 | 0.9216 | 1.0000 |
| 2026-02-24 20:21:52.556710 | mistral | BAAI/bge-small-en-v1.5 | nq | faiss | 15 | 3 | 0.9214 | 1.0000 |
| 2026-02-24 11:41:01.742230 | mistral | BAAI/bge-small-en-v1.5 | msmarco | bm25 | 15 | 3 | 0.9166 | 1.0000 |
| 2026-02-24 10:19:04.337640 | mistral | sentence-transformers/all-MiniLM-L6-v2 | msmarco | bm25 | 15 | 3 | 0.9166 | 1.0000 |
| 2026-02-24 00:58:15.455564 | mistral | BAAI/bge-small-en-v1.5 | healthcaremagic | faiss | 5 | 3 | 0.9162 | 1.0000 |
| 2026-02-24 10:46:17.325790 | mistral | BAAI/bge-small-en-v1.5 | msmarco | faiss | 10 | 3 | 0.9160 | 1.0000 |
| 2026-02-24 21:50:13.111283 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | nq | faiss | 5 | 5 | 0.9134 | 1.0000 |
| 2026-02-24 12:00:51.000088 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | faiss | 5 | 3 | 0.9100 | 1.0000 |
| 2026-02-23 23:19:29.854753 | mistral | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | faiss | 5 | 3 | 0.9088 | 1.0000 |
| 2026-02-24 19:44:13.487604 | mistral | sentence-transformers/all-MiniLM-L6-v2 | nq | bm25 | 15 | 5 | 0.9078 | 1.0000 |
| 2026-02-24 21:34:33.841007 | mistral | BAAI/bge-small-en-v1.5 | nq | bm25 | 15 | 5 | 0.9078 | 1.0000 |
| 2026-02-24 20:13:29.798314 | mistral | BAAI/bge-small-en-v1.5 | nq | faiss | 10 | 5 | 0.9076 | 1.0000 |
| 2026-02-23 23:24:38.495946 | mistral | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | faiss | 5 | 5 | 0.9050 | 1.0000 |
| 2026-02-24 10:05:21.110120 | mistral | sentence-transformers/all-MiniLM-L6-v2 | msmarco | bm25 | 10 | 3 | 0.9028 | 1.0000 |
| 2026-02-24 11:27:15.184966 | mistral | BAAI/bge-small-en-v1.5 | msmarco | bm25 | 10 | 3 | 0.9028 | 1.0000 |
| 2026-02-24 11:50:37.042197 | mistral | BAAI/bge-small-en-v1.5 | msmarco | bm25 | 15 | 5 | 0.9022 | 1.0000 |
| 2026-02-24 10:28:34.663735 | mistral | sentence-transformers/all-MiniLM-L6-v2 | msmarco | bm25 | 15 | 5 | 0.9022 | 1.0000 |
| 2026-02-24 09:38:17.683173 | mistral | sentence-transformers/all-MiniLM-L6-v2 | msmarco | faiss | 15 | 3 | 0.9020 | 1.0000 |
| 2026-02-24 19:55:09.669181 | mistral | BAAI/bge-small-en-v1.5 | nq | faiss | 5 | 3 | 0.8984 | 1.0000 |
| 2026-02-24 21:45:35.499066 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | nq | faiss | 5 | 3 | 0.8982 | 1.0000 |
| 2026-02-24 00:13:54.515512 | mistral | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | bm25 | 5 | 5 | 0.8970 | 1.0000 |
| 2026-02-24 01:52:24.565277 | mistral | BAAI/bge-small-en-v1.5 | healthcaremagic | bm25 | 5 | 5 | 0.8970 | 1.0000 |
| 2026-02-24 01:03:11.502562 | mistral | BAAI/bge-small-en-v1.5 | healthcaremagic | faiss | 5 | 5 | 0.8968 | 1.0000 |
| 2026-02-24 09:24:32.727478 | mistral | sentence-transformers/all-MiniLM-L6-v2 | msmarco | faiss | 10 | 3 | 0.8936 | 1.0000 |
| 2026-02-24 18:58:42.949432 | mistral | sentence-transformers/all-MiniLM-L6-v2 | nq | bm25 | 5 | 5 | 0.8924 | 1.0000 |
| 2026-02-24 20:48:59.369617 | mistral | BAAI/bge-small-en-v1.5 | nq | bm25 | 5 | 5 | 0.8924 | 1.0000 |
| 2026-02-24 09:47:55.189216 | mistral | sentence-transformers/all-MiniLM-L6-v2 | msmarco | faiss | 15 | 5 | 0.8898 | 1.0000 |
| 2026-02-24 18:54:10.207876 | mistral | sentence-transformers/all-MiniLM-L6-v2 | nq | bm25 | 5 | 3 | 0.8866 | 1.0000 |
| 2026-02-24 20:44:27.833163 | mistral | BAAI/bge-small-en-v1.5 | nq | bm25 | 5 | 3 | 0.8866 | 1.0000 |
| 2026-02-24 11:34:02.062026 | mistral | BAAI/bge-small-en-v1.5 | msmarco | bm25 | 10 | 5 | 0.8802 | 1.0000 |
| 2026-02-24 10:12:04.820312 | mistral | sentence-transformers/all-MiniLM-L6-v2 | msmarco | bm25 | 10 | 5 | 0.8802 | 1.0000 |
| 2026-02-24 18:22:37.825856 | mistral | sentence-transformers/all-MiniLM-L6-v2 | nq | faiss | 10 | 5 | 0.8778 | 1.0000 |
| 2026-02-24 11:09:50.180151 | mistral | BAAI/bge-small-en-v1.5 | msmarco | faiss | 15 | 5 | 0.8664 | 1.0000 |
| 2026-02-24 11:19:47.611932 | mistral | BAAI/bge-small-en-v1.5 | msmarco | bm25 | 5 | 3 | 0.8642 | 1.0000 |
| 2026-02-24 09:57:52.371994 | mistral | sentence-transformers/all-MiniLM-L6-v2 | msmarco | bm25 | 5 | 3 | 0.8642 | 1.0000 |
| 2026-02-24 10:01:31.281444 | mistral | sentence-transformers/all-MiniLM-L6-v2 | msmarco | bm25 | 5 | 5 | 0.8626 | 1.0000 |
| 2026-02-24 11:23:26.194442 | mistral | BAAI/bge-small-en-v1.5 | msmarco | bm25 | 5 | 5 | 0.8626 | 1.0000 |
| 2026-02-24 09:16:52.785847 | mistral | sentence-transformers/all-MiniLM-L6-v2 | msmarco | faiss | 5 | 3 | 0.8624 | 1.0000 |
| 2026-02-24 18:05:28.698034 | mistral | sentence-transformers/all-MiniLM-L6-v2 | nq | faiss | 5 | 3 | 0.8616 | 1.0000 |
| 2026-02-24 09:31:23.019787 | mistral | sentence-transformers/all-MiniLM-L6-v2 | msmarco | faiss | 10 | 5 | 0.8514 | 1.0000 |
| 2026-02-24 19:25:08.756662 | mistral | sentence-transformers/all-MiniLM-L6-v2 | nq | bm25 | 10 | 5 | 0.8480 | 1.0000 |
| 2026-02-24 21:15:31.790381 | mistral | BAAI/bge-small-en-v1.5 | nq | bm25 | 10 | 5 | 0.8480 | 1.0000 |
| 2026-02-24 10:38:45.633466 | mistral | BAAI/bge-small-en-v1.5 | msmarco | faiss | 5 | 3 | 0.8454 | 1.0000 |
| 2026-02-24 10:53:07.518530 | mistral | BAAI/bge-small-en-v1.5 | msmarco | faiss | 10 | 5 | 0.8432 | 1.0000 |
| 2026-02-24 20:00:12.103399 | mistral | BAAI/bge-small-en-v1.5 | nq | faiss | 5 | 5 | 0.8262 | 1.0000 |
| 2026-02-24 18:10:00.275796 | mistral | sentence-transformers/all-MiniLM-L6-v2 | nq | faiss | 5 | 5 | 0.8156 | 1.0000 |
| 2026-02-24 09:20:38.593960 | mistral | sentence-transformers/all-MiniLM-L6-v2 | msmarco | faiss | 5 | 5 | 0.8052 | 1.0000 |
| 2026-02-24 10:42:26.879703 | mistral | BAAI/bge-small-en-v1.5 | msmarco | faiss | 5 | 5 | 0.7966 | 1.0000 |
| 2026-02-24 20:33:02.215833 | mistral | BAAI/bge-small-en-v1.5 | nq | faiss | 15 | 5 | 0.7960 | 1.0000 |
| 2026-02-24 18:42:31.960500 | mistral | sentence-transformers/all-MiniLM-L6-v2 | nq | faiss | 15 | 5 | 0.7778 | 1.0000 |
| 2026-02-24 01:16:44.986644 | mistral | BAAI/bge-small-en-v1.5 | healthcaremagic | faiss | 10 | 5 | 0.7682 | 1.0000 |
| 2026-02-23 23:29:55.511326 | mistral | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | faiss | 10 | 3 | 0.7478 | 1.0000 |
| 2026-02-23 23:38:09.791294 | mistral | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | faiss | 10 | 5 | 0.7450 | 1.0000 |
| 2026-02-24 00:19:17.096980 | mistral | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | bm25 | 10 | 3 | 0.7312 | 1.0000 |
| 2026-02-24 01:57:47.002978 | mistral | BAAI/bge-small-en-v1.5 | healthcaremagic | bm25 | 10 | 3 | 0.7312 | 1.0000 |
| 2026-02-24 01:08:27.264030 | mistral | BAAI/bge-small-en-v1.5 | healthcaremagic | faiss | 10 | 3 | 0.7298 | 1.0000 |
| 2026-02-24 00:27:22.548979 | mistral | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | bm25 | 10 | 5 | 0.7236 | 1.0000 |
| 2026-02-24 02:05:50.743519 | mistral | BAAI/bge-small-en-v1.5 | healthcaremagic | bm25 | 10 | 5 | 0.7236 | 1.0000 |
| 2026-02-24 02:25:22.857173 | mistral | BAAI/bge-small-en-v1.5 | healthcaremagic | bm25 | 15 | 5 | 0.7142 | 1.0000 |
| 2026-02-24 00:46:50.200479 | mistral | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | bm25 | 15 | 5 | 0.7142 | 1.0000 |
| 2026-02-23 23:57:27.493795 | mistral | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | faiss | 15 | 5 | 0.6866 | 1.0000 |
| 2026-02-24 01:36:08.307012 | mistral | BAAI/bge-small-en-v1.5 | healthcaremagic | faiss | 15 | 5 | 0.6760 | 1.0000 |
| 2026-02-24 01:25:15.923447 | mistral | BAAI/bge-small-en-v1.5 | healthcaremagic | faiss | 15 | 3 | 0.6150 | 1.0000 |
| 2026-02-24 02:14:24.580294 | mistral | BAAI/bge-small-en-v1.5 | healthcaremagic | bm25 | 15 | 3 | 0.5630 | 1.0000 |
| 2026-02-24 00:35:57.129797 | mistral | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | bm25 | 15 | 3 | 0.5630 | 1.0000 |
| 2026-02-23 23:46:37.330304 | mistral | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | faiss | 15 | 3 | 0.5208 | 1.0000 |
| 2026-02-24 03:40:35.960705 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | bm25 | 5 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 03:48:34.106924 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | bm25 | 5 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 03:29:12.984896 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | faiss | 15 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 03:56:25.919150 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | bm25 | 10 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 04:07:01.624572 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | bm25 | 10 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 04:17:33.442208 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | bm25 | 15 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 04:28:25.674797 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | bm25 | 15 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 04:39:16.885612 | phi3 | BAAI/bge-small-en-v1.5 | healthcaremagic | faiss | 5 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 04:47:57.138362 | phi3 | BAAI/bge-small-en-v1.5 | healthcaremagic | faiss | 5 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 04:56:46.015052 | phi3 | BAAI/bge-small-en-v1.5 | healthcaremagic | faiss | 10 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 05:07:19.514009 | phi3 | BAAI/bge-small-en-v1.5 | healthcaremagic | faiss | 10 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 05:17:50.463662 | phi3 | BAAI/bge-small-en-v1.5 | healthcaremagic | faiss | 15 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 05:29:59.166474 | phi3 | BAAI/bge-small-en-v1.5 | healthcaremagic | faiss | 15 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 05:42:03.313521 | phi3 | BAAI/bge-small-en-v1.5 | healthcaremagic | bm25 | 5 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 05:49:58.908777 | phi3 | BAAI/bge-small-en-v1.5 | healthcaremagic | bm25 | 5 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 05:57:47.714697 | phi3 | BAAI/bge-small-en-v1.5 | healthcaremagic | bm25 | 10 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 06:08:22.254156 | phi3 | BAAI/bge-small-en-v1.5 | healthcaremagic | bm25 | 10 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 06:18:58.412028 | phi3 | BAAI/bge-small-en-v1.5 | healthcaremagic | bm25 | 15 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 06:29:48.076009 | phi3 | BAAI/bge-small-en-v1.5 | healthcaremagic | bm25 | 15 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 03:17:50.776637 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | faiss | 15 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 02:50:38.539121 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | faiss | 5 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 02:58:48.345629 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | faiss | 10 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 03:08:18.803799 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | faiss | 10 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 12:28:53.730887 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | faiss | 10 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 12:21:31.862542 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | faiss | 10 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 12:12:58.340374 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | faiss | 5 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 12:37:30.283493 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | faiss | 15 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 13:01:01.970094 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | bm25 | 5 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 12:56:30.642285 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | bm25 | 5 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 12:46:05.911134 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | faiss | 15 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 13:32:10.615960 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | bm25 | 15 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 13:42:13.157461 | phi3 | BAAI/bge-small-en-v1.5 | msmarco | faiss | 5 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 13:46:52.426370 | phi3 | BAAI/bge-small-en-v1.5 | msmarco | faiss | 5 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 13:53:08.178999 | phi3 | BAAI/bge-small-en-v1.5 | msmarco | faiss | 10 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 14:00:49.887700 | phi3 | BAAI/bge-small-en-v1.5 | msmarco | faiss | 10 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 14:08:25.991664 | phi3 | BAAI/bge-small-en-v1.5 | msmarco | faiss | 15 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 14:16:06.238961 | phi3 | BAAI/bge-small-en-v1.5 | msmarco | faiss | 15 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 14:25:17.287230 | phi3 | BAAI/bge-small-en-v1.5 | msmarco | bm25 | 5 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 14:29:24.895861 | phi3 | BAAI/bge-small-en-v1.5 | msmarco | bm25 | 5 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 14:34:49.181161 | phi3 | BAAI/bge-small-en-v1.5 | msmarco | bm25 | 10 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 14:40:29.489702 | phi3 | BAAI/bge-small-en-v1.5 | msmarco | bm25 | 10 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 14:47:29.291660 | phi3 | BAAI/bge-small-en-v1.5 | msmarco | bm25 | 15 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 14:55:40.364983 | phi3 | BAAI/bge-small-en-v1.5 | msmarco | bm25 | 15 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 13:08:54.174046 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | bm25 | 10 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 13:15:33.869369 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | bm25 | 10 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 13:24:04.180331 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | bm25 | 15 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 22:10:20.787995 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | nq | faiss | 10 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 22:20:09.219046 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | nq | faiss | 15 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 22:31:19.603145 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | nq | faiss | 15 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 22:42:34.768701 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | nq | bm25 | 5 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 22:49:03.626965 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | nq | bm25 | 5 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 22:55:47.004705 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | nq | bm25 | 10 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 23:04:28.556278 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | nq | bm25 | 10 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 23:12:29.216226 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | nq | bm25 | 15 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 23:22:29.424442 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | nq | bm25 | 15 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 23:33:01.019386 | phi3 | BAAI/bge-small-en-v1.5 | nq | faiss | 5 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 23:40:40.612732 | phi3 | BAAI/bge-small-en-v1.5 | nq | faiss | 5 | 5 | 0.5000 | 1.0000 |
| 2026-02-24 23:48:18.526181 | phi3 | BAAI/bge-small-en-v1.5 | nq | faiss | 10 | 3 | 0.5000 | 1.0000 |
| 2026-02-24 23:57:07.032625 | phi3 | BAAI/bge-small-en-v1.5 | nq | faiss | 10 | 5 | 0.5000 | 1.0000 |
| 2026-02-25 00:05:37.209162 | phi3 | BAAI/bge-small-en-v1.5 | nq | faiss | 15 | 3 | 0.5000 | 1.0000 |
| 2026-02-25 00:16:03.193881 | phi3 | BAAI/bge-small-en-v1.5 | nq | faiss | 15 | 5 | 0.5000 | 1.0000 |
| 2026-02-25 00:27:06.560922 | phi3 | BAAI/bge-small-en-v1.5 | nq | bm25 | 5 | 3 | 0.5000 | 1.0000 |
| 2026-02-25 00:33:51.635889 | phi3 | BAAI/bge-small-en-v1.5 | nq | bm25 | 5 | 5 | 0.5000 | 1.0000 |
| 2026-02-25 00:40:34.135551 | phi3 | BAAI/bge-small-en-v1.5 | nq | bm25 | 10 | 3 | 0.5000 | 1.0000 |
| 2026-02-25 00:48:39.817047 | phi3 | BAAI/bge-small-en-v1.5 | nq | bm25 | 10 | 5 | 0.5000 | 1.0000 |
| 2026-02-25 00:56:52.341678 | phi3 | BAAI/bge-small-en-v1.5 | nq | bm25 | 15 | 3 | 0.5000 | 1.0000 |
| 2026-02-25 01:07:37.665199 | phi3 | BAAI/bge-small-en-v1.5 | nq | bm25 | 15 | 5 | 0.5000 | 1.0000 |