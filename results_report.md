# Experiment Results Analysis

## 1. Overall Best Performance

The highest AUC achieving configuration was:
- **LLM**: `llama3`
- **Embedding**: `sentence-transformers/all-MiniLM-L6-v2`
- **Retriever**: `faiss`
- **Dataset**: `healthcaremagic`
- **AUC**: **0.9946**

## 2. Performance by LLM

| LLM | AUC | Retrieval Recall |
| --- | --- | --- |
| llama3 | 0.9434 | 1.0000 |
| mistral | 0.7833 | 1.0000 |
| phi3 | 0.7117 | 1.0000 |

## 3. Performance by Embedding Model

| Embedding | AUC | Retrieval Recall |
| --- | --- | --- |
| sentence-transformers/all-MiniLM-L6-v2 | 0.8486 | 1.0000 |
| BAAI/bge-small-en-v1.5 | 0.7770 | 1.0000 |

## 4. Performance by Retriever

| Retriever | AUC | Retrieval Recall |
| --- | --- | --- |
| faiss | 0.8376 | 1.0000 |
| bm25 | 0.7880 | 1.0000 |

## 5. Dataset Difficulty (Average AUC)

| Dataset | AUC | Retrieval Recall |
| --- | --- | --- |
| nq | 0.7929 | 1.0000 |
| healthcaremagic | 0.8135 | 1.0000 |
| msmarco | 0.8319 | 1.0000 |

## 6. All Experiment Runs

| Timestamp | LLM | Embedding | Dataset | Retriever | AUC | Retrieval Recall |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-01-25 23:05:24 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | faiss | 0.9946 | 1.0000 |
| 2026-01-25 23:19:15 | llama3 | BAAI/bge-small-en-v1.5 | healthcaremagic | faiss | 0.9930 | 1.0000 |
| 2026-01-25 23:12:23 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | bm25 | 0.9608 | 1.0000 |
| 2026-01-25 23:26:07 | llama3 | BAAI/bge-small-en-v1.5 | healthcaremagic | bm25 | 0.9608 | 1.0000 |
| 2026-01-25 23:59:53 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | faiss | 0.9600 | 1.0000 |
| 2026-01-26 00:44:54 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | bm25 | 0.9468 | 1.0000 |
| 2026-01-26 00:54:11 | llama3 | BAAI/bge-small-en-v1.5 | msmarco | bm25 | 0.9468 | 1.0000 |
| 2026-01-26 00:40:11 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | faiss | 0.9452 | 1.0000 |
| 2026-01-26 00:49:24 | llama3 | BAAI/bge-small-en-v1.5 | msmarco | faiss | 0.9396 | 1.0000 |
| 2026-01-26 02:26:53 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | nq | bm25 | 0.9298 | 1.0000 |
| 2026-01-26 01:51:11 | llama3 | BAAI/bge-small-en-v1.5 | nq | bm25 | 0.9282 | 1.0000 |
| 2026-01-26 01:40:10 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | nq | bm25 | 0.9282 | 1.0000 |
| 2026-01-26 01:34:26 | llama3 | sentence-transformers/all-MiniLM-L6-v2 | nq | faiss | 0.9226 | 1.0000 |
| 2026-01-25 23:46:12 | mistral | BAAI/bge-small-en-v1.5 | healthcaremagic | faiss | 0.9112 | 1.0000 |
| 2026-01-25 23:32:47 | mistral | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | faiss | 0.9104 | 1.0000 |
| 2026-01-26 02:20:23 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | nq | faiss | 0.9090 | 1.0000 |
| 2026-01-26 01:45:28 | llama3 | BAAI/bge-small-en-v1.5 | nq | faiss | 0.8540 | 1.0000 |
| 2026-01-26 01:25:46 | phi3 | BAAI/bge-small-en-v1.5 | msmarco | faiss | 0.8478 | 1.0000 |
| 2026-01-26 01:17:14 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | faiss | 0.8206 | 1.0000 |
| 2026-01-26 02:08:36 | mistral | BAAI/bge-small-en-v1.5 | nq | faiss | 0.8084 | 1.0000 |
| 2026-01-26 01:21:17 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | msmarco | bm25 | 0.7864 | 1.0000 |
| 2026-01-26 01:29:58 | phi3 | BAAI/bge-small-en-v1.5 | msmarco | bm25 | 0.7864 | 1.0000 |
| 2026-01-25 23:39:21 | mistral | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | bm25 | 0.7858 | 1.0000 |
| 2026-01-25 23:53:11 | mistral | BAAI/bge-small-en-v1.5 | healthcaremagic | bm25 | 0.7858 | 1.0000 |
| 2026-01-26 00:58:39 | mistral | sentence-transformers/all-MiniLM-L6-v2 | msmarco | faiss | 0.7686 | 1.0000 |
| 2026-01-26 01:08:12 | mistral | BAAI/bge-small-en-v1.5 | msmarco | faiss | 0.7554 | 1.0000 |
| 2026-01-26 02:14:33 | mistral | BAAI/bge-small-en-v1.5 | nq | bm25 | 0.7492 | 1.0000 |
| 2026-01-26 02:02:47 | mistral | sentence-transformers/all-MiniLM-L6-v2 | nq | bm25 | 0.7492 | 1.0000 |
| 2026-01-26 01:56:31 | mistral | sentence-transformers/all-MiniLM-L6-v2 | nq | faiss | 0.7362 | 1.0000 |
| 2026-01-26 01:03:40 | mistral | sentence-transformers/all-MiniLM-L6-v2 | msmarco | bm25 | 0.7198 | 1.0000 |
| 2026-01-26 01:12:52 | mistral | BAAI/bge-small-en-v1.5 | msmarco | bm25 | 0.7198 | 1.0000 |
| 2026-01-26 00:31:47 | phi3 | BAAI/bge-small-en-v1.5 | healthcaremagic | bm25 | 0.5000 | 1.0000 |
| 2026-01-26 00:22:30 | phi3 | BAAI/bge-small-en-v1.5 | healthcaremagic | faiss | 0.5000 | 1.0000 |
| 2026-01-26 00:14:12 | phi3 | sentence-transformers/all-MiniLM-L6-v2 | healthcaremagic | bm25 | 0.5000 | 1.0000 |
| 2026-01-26 02:39:12 | phi3 | BAAI/bge-small-en-v1.5 | nq | faiss | 0.5000 | 1.0000 |
| 2026-01-26 02:47:11 | phi3 | BAAI/bge-small-en-v1.5 | nq | bm25 | 0.5000 | 1.0000 |