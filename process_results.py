import argparse
import numbers
import os
import re

import pandas as pd

EXPERIMENT_FILE = "experiment_results.md"
CSV_FILE = "experiment_data.csv"
REPORT_FILE = "results_report.md"

COLUMN_ORDER = [
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


def _parse_config_values(config_text):
    parsed = {}
    match = re.search(r"Config\((.*)\)", config_text)
    if not match:
        return parsed

    config_body = match.group(1).strip()
    for key, value in re.findall(r"(\w+)\s*=\s*(.*?)(?=,\s*\w+\s*=|$)", config_body):
        parsed[key.strip()] = value.strip()
    return parsed


def parse_experiment_results(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    experiments = re.split(r"## Run ", content)
    data = []

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
    }

    for exp in experiments:
        exp = exp.strip()
        if not exp:
            continue

        timestamp_match = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?)", exp)
        timestamp = timestamp_match.group(1) if timestamp_match else "Unknown"

        row = {col: None for col in COLUMN_ORDER}
        row["Timestamp"] = timestamp

        field_pairs = re.findall(r"- \*\*(.+?)\*\*: (.*)", exp)
        fields = {k.strip(): v.strip() for k, v in field_pairs}

        config_raw = fields.get("Config")
        if config_raw:
            config_values = _parse_config_values(config_raw)
            for key, mapped_key in config_key_map.items():
                if key in config_values:
                    row[mapped_key] = config_values[key]

        for key, mapped_key in bullet_key_map.items():
            if key in fields:
                row[mapped_key] = fields[key]

        if row["AUC"] is None:
            continue

        data.append(row)

    df = pd.DataFrame(data, columns=COLUMN_ORDER)
    if df.empty:
        return df

    for col in ["AUC", "Retrieval Recall", "Num Masks", "Retriever K", "Index Size"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def to_markdown_table(df):
    if df.empty:
        return ""

    headers = list(df.columns)
    header_row = "| " + " | ".join(headers) + " |"
    sep_row = "| " + " | ".join(["---"] * len(headers)) + " |"

    rows = []
    for _, row in df.iterrows():
        formatted_row = []
        for val in row:
            if pd.isna(val):
                formatted_row.append("")
            elif isinstance(val, numbers.Integral):
                formatted_row.append(str(int(val)))
            elif isinstance(val, numbers.Real):
                formatted_row.append(f"{float(val):.4f}")
            else:
                formatted_row.append(str(val))
        rows.append("| " + " | ".join(formatted_row) + " |")

    return "\n".join([header_row, sep_row] + rows)


def _group_mean(df, group_col, sort_col="AUC", ascending=False):
    subset = df.dropna(subset=[group_col, "AUC"])
    if subset.empty:
        return pd.DataFrame(columns=[group_col, "AUC", "Retrieval Recall"])

    grouped = (
        subset.groupby(group_col)[["AUC", "Retrieval Recall"]]
        .mean()
        .reset_index()
        .sort_values(by=sort_col, ascending=ascending)
    )
    return grouped


def _safe_value(value):
    if value is None or pd.isna(value):
        return "Unknown"
    return value


def generate_report(df, output_path):
    report_content = "# Experiment Results Analysis\n\n"

    scored_df = df.dropna(subset=["AUC"])
    if scored_df.empty:
        report_content += "No runs with valid AUC were found.\n"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"Report generated at {output_path}")
        return

    best_run = scored_df.loc[scored_df["AUC"].idxmax()]
    report_content += "## 1. Overall Best Performance\n\n"
    report_content += "The highest AUC achieving configuration was:\n"
    report_content += f"- **LLM**: `{_safe_value(best_run['LLM'])}`\n"
    report_content += f"- **Embedding**: `{_safe_value(best_run['Embedding'])}`\n"
    report_content += f"- **Retriever**: `{_safe_value(best_run['Retriever'])}`\n"
    report_content += f"- **Dataset**: `{_safe_value(best_run['Dataset'])}`\n"
    if not pd.isna(best_run["Num Masks"]):
        report_content += f"- **Num Masks**: `{int(best_run['Num Masks'])}`\n"
    if not pd.isna(best_run["Retriever K"]):
        report_content += f"- **Retriever K**: `{int(best_run['Retriever K'])}`\n"
    report_content += f"- **AUC**: **{best_run['AUC']:.4f}**\n\n"

    report_content += "## 2. Performance by LLM\n\n"
    llm_stats = _group_mean(scored_df, "LLM", sort_col="AUC", ascending=False)
    report_content += to_markdown_table(llm_stats) + "\n\n"

    report_content += "## 3. Performance by Embedding Model\n\n"
    emb_stats = _group_mean(scored_df, "Embedding", sort_col="AUC", ascending=False)
    report_content += to_markdown_table(emb_stats) + "\n\n"

    report_content += "## 4. Performance by Retriever\n\n"
    ret_stats = _group_mean(scored_df, "Retriever", sort_col="AUC", ascending=False)
    report_content += to_markdown_table(ret_stats) + "\n\n"

    report_content += "## 5. Dataset Difficulty (Average AUC)\n\n"
    data_stats = _group_mean(scored_df, "Dataset", sort_col="AUC", ascending=True)
    report_content += to_markdown_table(data_stats) + "\n\n"

    report_content += "## 6. Performance by Num Masks\n\n"
    mask_stats = _group_mean(scored_df, "Num Masks", sort_col="Num Masks", ascending=True)
    report_content += to_markdown_table(mask_stats) + "\n\n"

    report_content += "## 7. Performance by Retriever K\n\n"
    k_stats = _group_mean(scored_df, "Retriever K", sort_col="Retriever K", ascending=True)
    report_content += to_markdown_table(k_stats) + "\n\n"

    report_content += "## 8. All Experiment Runs\n\n"
    display_cols = [
        "Timestamp",
        "LLM",
        "Embedding",
        "Dataset",
        "Retriever",
        "Num Masks",
        "Retriever K",
        "AUC",
        "Retrieval Recall",
    ]
    display_df = scored_df[display_cols].sort_values(by="AUC", ascending=False, na_position="last")
    report_content += to_markdown_table(display_df)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"Report generated at {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Parse MBA experiment markdown logs and generate summaries.")
    parser.add_argument("--input", default=EXPERIMENT_FILE, help="Input experiment markdown file path.")
    parser.add_argument("--csv", default=CSV_FILE, help="Output CSV file path.")
    parser.add_argument("--report", default=REPORT_FILE, help="Output markdown report path.")
    args = parser.parse_args()

    print("Starting process_results.py...")
    if not os.path.exists(args.input):
        print(f"Error: {args.input} not found.")
        return

    print(f"Parsing {args.input}...")
    df = parse_experiment_results(args.input)

    if df.empty:
        print("No data extracted. Check file format or parser assumptions.")
        return

    df.to_csv(args.csv, index=False)
    print(f"Extracted {len(df)} runs to {args.csv}")

    print(f"Generating report to {args.report}...")
    generate_report(df, args.report)
    print("Done.")


if __name__ == "__main__":
    main()
