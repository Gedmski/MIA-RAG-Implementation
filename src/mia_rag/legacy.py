from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


LEGACY_COMPAT_COLUMNS = [
    "Timestamp",
    "LLM",
    "Dataset",
    "Embedding",
    "Retriever",
    "Num Masks",
    "Retriever K",
    "Index Size",
    "Eval Samples",
    "AUC",
    "Retrieval Recall",
]


def _parse_config_values(config_text: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    match = re.search(r"Config\((.*)\)", config_text)
    if not match:
        return parsed
    config_body = match.group(1).strip()
    for key, value in re.findall(r"(\w+)\s*=\s*(.*?)(?=,\s*\w+\s*=|$)", config_body):
        parsed[key.strip()] = value.strip()
    return parsed


def parse_legacy_markdown(path: str | Path) -> pd.DataFrame:
    content = Path(path).read_text(encoding="utf-8")
    experiments = re.split(r"## Run ", content)
    rows: list[dict[str, object]] = []

    config_key_map = {
        "LLM": "LLM",
        "Data": "Dataset",
        "Emb": "Embedding",
        "Ret": "Retriever",
        "Idx": "Index Size",
        "Eval": "Eval Samples",
        "M": "Num Masks",
        "K": "Retriever K",
    }
    bullet_key_map = {
        "LLM": "LLM",
        "Dataset": "Dataset",
        "Embedding": "Embedding",
        "Retriever": "Retriever",
        "Num Masks": "Num Masks",
        "Retriever K": "Retriever K",
        "Index Size": "Index Size",
        "Eval Samples": "Eval Samples",
        "Samples": "Eval Samples",
        "AUC": "AUC",
        "Retrieval Recall": "Retrieval Recall",
        "Error": "Error",
    }

    for experiment in experiments:
        experiment = experiment.strip()
        if not experiment:
            continue
        timestamp_match = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?)", experiment)
        timestamp = timestamp_match.group(1) if timestamp_match else "Unknown"
        row: dict[str, object] = {column: None for column in LEGACY_COMPAT_COLUMNS}
        row["Timestamp"] = timestamp

        field_pairs = re.findall(r"- \*\*(.+?)\*\*: (.*)", experiment)
        fields = {key.strip(): value.strip() for key, value in field_pairs}
        config_raw = fields.get("Config")
        if config_raw:
            config_values = _parse_config_values(config_raw)
            for key, mapped in config_key_map.items():
                if key in config_values:
                    row[mapped] = config_values[key]
        for key, mapped in bullet_key_map.items():
            if key in fields:
                row[mapped] = fields[key]
        if row["AUC"] is None and "Error" not in row:
            continue
        rows.append(row)

    dataframe = pd.DataFrame(rows, columns=LEGACY_COMPAT_COLUMNS + ["Error"])
    if dataframe.empty:
        return dataframe

    for column in ["AUC", "Retrieval Recall", "Num Masks", "Retriever K", "Index Size"]:
        dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce")
    return dataframe


def structured_to_compat_df(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe.empty:
        return pd.DataFrame(columns=LEGACY_COMPAT_COLUMNS)
    compat = pd.DataFrame(
        {
            "Timestamp": dataframe["started_at"],
            "LLM": dataframe["llm_model"],
            "Dataset": dataframe["dataset"],
            "Embedding": dataframe["embedding_model"],
            "Retriever": dataframe["retriever_type"],
            "Num Masks": dataframe["num_masks"],
            "Retriever K": dataframe["retriever_k"],
            "Index Size": dataframe["index_size"],
            "Eval Samples": dataframe["member_samples"].fillna(0).astype(int).astype(str)
            + " (M:"
            + dataframe["member_samples"].fillna(0).astype(int).astype(str)
            + ", NM:"
            + dataframe["non_member_samples"].fillna(0).astype(int).astype(str)
            + ")",
            "AUC": dataframe["auc"],
            "Retrieval Recall": dataframe["retrieval_recall"],
        }
    )
    return compat[LEGACY_COMPAT_COLUMNS]


def render_legacy_markdown(dataframe: pd.DataFrame) -> str:
    if dataframe.empty:
        return "# Experiment Results\n\nNo successful runs were found.\n"

    lines = []
    for _, row in dataframe.iterrows():
        lines.append(f"## Run {row['started_at']}")
        lines.append(
            "- **Config**: "
            f"Config(LLM={row['llm_model']}, Data={row['dataset']}, Emb={row['embedding_model']}, "
            f"Ret={row['retriever_type']}, M={int(row['num_masks'])}, K={int(row['retriever_k'])}, "
            f"Idx={int(row['index_size'])}, Eval={int(row['eval_size'])})"
        )
        lines.append(f"- **Num Masks**: {int(row['num_masks'])}")
        lines.append(f"- **Retriever K**: {int(row['retriever_k'])}")
        lines.append(f"- **AUC**: {float(row['auc']):.4f}")
        lines.append(f"- **Retrieval Recall**: {float(row['retrieval_recall']):.4f}")
        lines.append(f"- **Index Size**: {int(row['index_size'])}")
        lines.append(
            f"- **Eval Samples**: {int(row['member_samples']) + int(row['non_member_samples'])} "
            f"(M:{int(row['member_samples'])}, NM:{int(row['non_member_samples'])})"
        )
        lines.append("---")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
