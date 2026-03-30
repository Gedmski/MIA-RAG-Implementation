from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd

from .legacy import LEGACY_COMPAT_COLUMNS, render_legacy_markdown, structured_to_compat_df


SUMMARY_COLUMNS = [
    "study_name",
    "run_name",
    "started_at",
    "finished_at",
    "status",
    "dataset",
    "dataset_loader",
    "model_provider",
    "llm_model",
    "llm_model_name",
    "embedding_model",
    "embedding_model_name",
    "retriever_type",
    "num_masks",
    "retriever_k",
    "gamma",
    "index_size",
    "eval_size",
    "member_samples",
    "non_member_samples",
    "auc",
    "accuracy",
    "precision",
    "recall",
    "f1",
    "retrieval_recall",
    "runtime_seconds",
    "failure_reason",
    "config_repr",
]
NUMERIC_COLUMNS = [
    "num_masks",
    "retriever_k",
    "gamma",
    "index_size",
    "eval_size",
    "member_samples",
    "non_member_samples",
    "auc",
    "accuracy",
    "precision",
    "recall",
    "f1",
    "retrieval_recall",
    "runtime_seconds",
]


def _coerce_numeric_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    for column in NUMERIC_COLUMNS:
        if column in dataframe.columns:
            dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce")
    return dataframe


def load_structured_records(path: str | Path) -> pd.DataFrame:
    source = Path(path)
    if source.is_dir():
        source = source / "runs.jsonl"
    if not source.exists():
        raise FileNotFoundError(f"Structured results not found: {source}")

    rows: list[dict] = []
    with source.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    dataframe = pd.DataFrame(rows)
    if dataframe.empty:
        return pd.DataFrame(columns=SUMMARY_COLUMNS)
    dataframe = _coerce_numeric_columns(dataframe)
    return dataframe.reindex(columns=SUMMARY_COLUMNS)


def write_structured_records(records: Iterable[dict], path: str | Path) -> None:
    with Path(path).open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")


def build_summary_dataframe(records: Iterable[dict]) -> pd.DataFrame:
    dataframe = pd.DataFrame(list(records))
    if dataframe.empty:
        return pd.DataFrame(columns=SUMMARY_COLUMNS)
    dataframe = _coerce_numeric_columns(dataframe)
    return dataframe.reindex(columns=SUMMARY_COLUMNS)


def _format_table(dataframe: pd.DataFrame) -> str:
    if dataframe.empty:
        return "_No data available._"
    display = dataframe.copy()
    for column in display.columns:
        if pd.api.types.is_numeric_dtype(display[column]):
            display[column] = display[column].map(
                lambda value: (
                    ""
                    if pd.isna(value)
                    else (f"{value:.4f}" if not float(value).is_integer() else str(int(value)))
                )
            )
    headers = [str(header) for header in display.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in display.iterrows():
        values = ["" if pd.isna(value) else str(value) for value in row]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def _successful_runs(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe.empty:
        return dataframe.copy()
    return dataframe[dataframe["status"] == "success"].copy()


def _has_multiple_studies(dataframe: pd.DataFrame) -> bool:
    study_names = [name for name in dataframe.get("study_name", pd.Series(dtype=str)).dropna().unique() if str(name).strip()]
    return len(study_names) > 1


def _metric_text(value: object) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{float(value):.4f}"


def _group_metric(dataframe: pd.DataFrame, group_by: list[str]) -> pd.DataFrame:
    subset = _successful_runs(dataframe).dropna(subset=["auc"])
    if subset.empty:
        return pd.DataFrame(columns=group_by + ["auc", "f1", "retrieval_recall"])
    grouped = (
        subset.groupby(group_by)[["auc", "f1", "retrieval_recall"]]
        .mean()
        .reset_index()
        .sort_values(["auc", "f1", "retrieval_recall"], ascending=[False, False, False])
    )
    return grouped


def _append_dataset_sections(lines: list[str], dataframe: pd.DataFrame) -> None:
    for dataset_name in sorted(dataframe["dataset"].dropna().unique()):
        dataset_frame = dataframe[dataframe["dataset"] == dataset_name].copy()
        lines.extend([f"## Dataset: {dataset_name}", ""])
        model_table = _group_metric(dataset_frame, ["llm_model"])
        lines.extend(
            [
                "### Model Comparison",
                "",
                _format_table(
                    model_table.rename(
                        columns={
                            "llm_model": "Model",
                            "auc": "AUC",
                            "f1": "F1",
                            "retrieval_recall": "Recall",
                        }
                    )
                ),
                "",
            ]
        )

        retriever_embedding = (
            dataset_frame.groupby(["retriever_type", "embedding_model"])[["auc", "f1", "retrieval_recall"]]
            .mean()
            .reset_index()
            .sort_values(["auc", "f1"], ascending=False)
        )
        lines.extend(
            [
                "### Retriever x Embedding",
                "",
                _format_table(
                    retriever_embedding.rename(
                        columns={
                            "retriever_type": "Retriever",
                            "embedding_model": "Embedding",
                            "auc": "AUC",
                            "f1": "F1",
                            "retrieval_recall": "Recall",
                        }
                    )
                ),
                "",
            ]
        )

        best_worst = (
            dataset_frame.sort_values("auc", ascending=False)[
                ["llm_model", "retriever_type", "embedding_model", "num_masks", "retriever_k", "gamma", "auc", "f1"]
            ]
        )
        lines.extend(
            [
                "### Best And Worst Configurations",
                "",
                _format_table(pd.concat([best_worst.head(3), best_worst.tail(3)], ignore_index=True)),
                "",
            ]
        )

        for model_name in sorted(dataset_frame["llm_model"].dropna().unique()):
            model_frame = dataset_frame[dataset_frame["llm_model"] == model_name]
            pivot = model_frame.pivot_table(
                index="num_masks",
                columns="retriever_k",
                values="auc",
                aggfunc="mean",
            ).sort_index().sort_index(axis=1)
            lines.extend([f"### M x K Matrix: {model_name}", "", _format_table(pivot.reset_index().rename(columns={"num_masks": "M"})), ""])


def generate_report(dataframe: pd.DataFrame, output_path: str | Path) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    successful = _successful_runs(dataframe)
    lines = ["# MBA Experiment Report", ""]

    if successful.empty:
        lines.append("No successful runs were found in the provided input.")
        output.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    best_row = successful.sort_values(["auc", "f1"], ascending=False).iloc[0]
    lines.extend(
        [
            "## Summary",
            "",
            f"- Successful runs: `{len(successful)}`",
            f"- Failed runs: `{int((dataframe['status'] == 'failed').sum())}`",
            f"- Best study/config: `{best_row['study_name']} / {best_row['dataset']} / {best_row['llm_model']} / {best_row['retriever_type']} / M={int(best_row['num_masks'])} / K={int(best_row['retriever_k'])} / gamma={_metric_text(best_row['gamma'])}`",
            f"- Best AUC: `{_metric_text(best_row['auc'])}`",
            f"- Best F1: `{_metric_text(best_row['f1'])}`",
            "",
        ]
    )

    if _has_multiple_studies(successful):
        study_summary = (
            successful.groupby("study_name")[["auc", "f1", "retrieval_recall"]]
            .mean()
            .reset_index()
            .sort_values(["auc", "f1"], ascending=False)
        )
        lines.extend(
            [
                "## Study Overview",
                "",
                _format_table(
                    study_summary.rename(
                        columns={
                            "study_name": "Study",
                            "auc": "AUC",
                            "f1": "F1",
                            "retrieval_recall": "Recall",
                        }
                    )
                ),
                "",
            ]
        )
        for study_name in sorted(successful["study_name"].dropna().unique()):
            study_frame = successful[successful["study_name"] == study_name].copy()
            lines.extend([f"## Study: {study_name}", ""])
            _append_dataset_sections(lines, study_frame)
    else:
        _append_dataset_sections(lines, successful)

    output.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def generate_plots(dataframe: pd.DataFrame, plots_dir: str | Path) -> None:
    plots_path = Path(plots_dir)
    plots_path.mkdir(parents=True, exist_ok=True)
    successful = _successful_runs(dataframe)
    if successful.empty:
        return

    if _has_multiple_studies(successful):
        study_summary = (
            successful.groupby("study_name")[["auc", "f1"]]
            .mean()
            .sort_values("auc", ascending=False)
        )
        if not study_summary.empty:
            plt.figure(figsize=(9, 4))
            study_summary["auc"].plot(kind="bar", color="#2f6db2")
            plt.title("Mean AUC by Study")
            plt.ylabel("AUC")
            plt.tight_layout()
            plt.savefig(plots_path / "study_auc_comparison.png")
            plt.close()

            plt.figure(figsize=(9, 4))
            study_summary["f1"].plot(kind="bar", color="#b24c2f")
            plt.title("Mean F1 by Study")
            plt.ylabel("F1")
            plt.tight_layout()
            plt.savefig(plots_path / "study_f1_comparison.png")
            plt.close()
        return

    for dataset_name in sorted(successful["dataset"].dropna().unique()):
        dataset_frame = successful[successful["dataset"] == dataset_name]

        model_summary = dataset_frame.groupby("llm_model")["auc"].mean().sort_values(ascending=False)
        if not model_summary.empty:
            plt.figure(figsize=(8, 4))
            model_summary.plot(kind="bar", color="#2f6db2")
            plt.title(f"{dataset_name}: Mean AUC by Model")
            plt.ylabel("AUC")
            plt.tight_layout()
            plt.savefig(plots_path / f"{dataset_name}_model_comparison.png")
            plt.close()

        recall_auc = dataset_frame.groupby("llm_model")[["retrieval_recall", "auc"]].mean().reset_index()
        if not recall_auc.empty:
            plt.figure(figsize=(6, 5))
            plt.scatter(recall_auc["retrieval_recall"], recall_auc["auc"], color="#b24c2f")
            for _, row in recall_auc.iterrows():
                plt.annotate(row["llm_model"], (row["retrieval_recall"], row["auc"]))
            plt.xlabel("Retrieval Recall")
            plt.ylabel("AUC")
            plt.title(f"{dataset_name}: Recall vs AUC")
            plt.tight_layout()
            plt.savefig(plots_path / f"{dataset_name}_recall_vs_auc.png")
            plt.close()

        for model_name in sorted(dataset_frame["llm_model"].dropna().unique()):
            model_frame = dataset_frame[dataset_frame["llm_model"] == model_name]
            pivot = model_frame.pivot_table(index="num_masks", columns="retriever_k", values="auc", aggfunc="mean")
            if not pivot.empty:
                plt.figure(figsize=(7, 5))
                plt.imshow(pivot.values, aspect="auto", cmap="viridis")
                plt.colorbar(label="AUC")
                plt.xticks(range(len(pivot.columns)), [str(column) for column in pivot.columns])
                plt.yticks(range(len(pivot.index)), [str(index) for index in pivot.index])
                plt.xlabel("K")
                plt.ylabel("M")
                plt.title(f"{dataset_name}: {model_name} M x K AUC")
                plt.tight_layout()
                plt.savefig(plots_path / f"{dataset_name}_{model_name}_heatmap.png")
                plt.close()

            if not model_frame.empty:
                mean_by_mask = model_frame.groupby(["num_masks", "retriever_k"])["auc"].mean().reset_index()
                plt.figure(figsize=(8, 5))
                for retriever_k, group in mean_by_mask.groupby("retriever_k"):
                    plt.plot(group["num_masks"], group["auc"], marker="o", label=f"K={int(retriever_k)}")
                plt.title(f"{dataset_name}: {model_name} AUC vs M")
                plt.xlabel("M")
                plt.ylabel("AUC")
                plt.legend()
                plt.tight_layout()
                plt.savefig(plots_path / f"{dataset_name}_{model_name}_auc_vs_m.png")
                plt.close()

                mean_by_k = model_frame.groupby(["retriever_k", "num_masks"])["auc"].mean().reset_index()
                plt.figure(figsize=(8, 5))
                for num_masks, group in mean_by_k.groupby("num_masks"):
                    plt.plot(group["retriever_k"], group["auc"], marker="o", label=f"M={int(num_masks)}")
                plt.title(f"{dataset_name}: {model_name} AUC vs K")
                plt.xlabel("K")
                plt.ylabel("AUC")
                plt.legend()
                plt.tight_layout()
                plt.savefig(plots_path / f"{dataset_name}_{model_name}_auc_vs_k.png")
                plt.close()


def write_summary_csv(dataframe: pd.DataFrame, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(path, index=False)


def write_legacy_snapshots(dataframe: pd.DataFrame, markdown_path: str | Path, csv_path: str | Path, report_path: str | Path) -> None:
    successful = _successful_runs(dataframe)
    compat_df = structured_to_compat_df(successful)
    Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
    compat_df.to_csv(csv_path, index=False)
    Path(markdown_path).write_text(render_legacy_markdown(successful), encoding="utf-8")
    generate_report(dataframe, report_path)


def compat_csv_columns() -> list[str]:
    return list(LEGACY_COMPAT_COLUMNS)
