from __future__ import annotations

import argparse
from pathlib import Path

from .legacy import parse_legacy_markdown
from .reporting import generate_plots, generate_report, load_structured_records, write_summary_csv, write_legacy_snapshots
from .runner import run_experiments


def run_cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run MBA RAG experiments from a YAML config.")
    parser.add_argument("--config", default="configs/default.yaml", help="Path to the experiment YAML config.")
    args = parser.parse_args(argv)
    run_dir = run_experiments(args.config)
    print(f"Run outputs written to {run_dir}")
    return 0


def _resolve_processing_output(input_path: Path, output_dir: str | None, csv: str | None, report: str | None) -> tuple[Path, Path, Path]:
    if output_dir:
        base = Path(output_dir)
        return base / "summary.csv", base / "report.md", base / "plots"
    if input_path.is_dir():
        return input_path / "summary.csv", input_path / "report.md", input_path / "plots"
    if input_path.name == "experiment_results.md":
        return Path(csv or "experiment_data.csv"), Path(report or "results_report.md"), Path("plots")
    base = input_path.parent
    return Path(csv) if csv else base / "summary.csv", Path(report) if report else base / "report.md", base / "plots"


def process_results_cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Process structured or legacy MBA results into reports.")
    parser.add_argument("--input", default="experiment_results.md", help="Run directory, runs.jsonl, or legacy markdown file.")
    parser.add_argument("--output-dir", help="Optional output directory for generated files.")
    parser.add_argument("--csv", help="Optional CSV path override.")
    parser.add_argument("--report", help="Optional markdown report path override.")
    parser.add_argument("--no-plots", action="store_true", help="Disable plot generation.")
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input path not found: {input_path}")

    if input_path.is_dir() or input_path.suffix == ".jsonl":
        dataframe = load_structured_records(input_path)
    else:
        legacy_df = parse_legacy_markdown(input_path)
        dataframe = legacy_df.rename(
            columns={
                "Timestamp": "started_at",
                "LLM": "llm_model",
                "Dataset": "dataset",
                "Embedding": "embedding_model",
                "Retriever": "retriever_type",
                "Num Masks": "num_masks",
                "Retriever K": "retriever_k",
                "Index Size": "index_size",
                "AUC": "auc",
                "Retrieval Recall": "retrieval_recall",
            }
        )
        dataframe["finished_at"] = dataframe.get("started_at", "")
        dataframe["status"] = dataframe.get("Error").fillna("").map(lambda value: "failed" if value else "success")
        dataframe["dataset_loader"] = ""
        dataframe["eval_size"] = ""
        dataframe["member_samples"] = 0
        dataframe["non_member_samples"] = 0
        dataframe["runtime_seconds"] = ""
        dataframe["failure_reason"] = dataframe.get("Error", "").fillna("")
        dataframe["config_repr"] = ""

    csv_path, report_path, plots_path = _resolve_processing_output(input_path, args.output_dir, args.csv, args.report)
    write_summary_csv(dataframe, csv_path)
    generate_report(dataframe, report_path)
    if not args.no_plots:
        generate_plots(dataframe, plots_path)
    if input_path.is_dir() or input_path.suffix == ".jsonl":
        write_legacy_snapshots(dataframe, "experiment_results.md", "experiment_data.csv", "results_report.md")
    print(f"Summary CSV written to {csv_path}")
    print(f"Report written to {report_path}")
    return 0
