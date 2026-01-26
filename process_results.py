import re
import pandas as pd
import os

EXPERIMENT_FILE = 'experiment_results.md'
CSV_FILE = 'experiment_data.csv'
REPORT_FILE = 'results_report.md'

def parse_experiment_results(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by experiment runs (## Run ...)
    experiments = re.split(r'## Run ', content)
    data = []

    for exp in experiments:
        if not exp.strip():
            continue

        # Extract timestamp (it's right after ## Run )
        # The split removes "## Run ", so the first chars are the timestamp
        timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', exp)
        timestamp = timestamp_match.group(1) if timestamp_match else "Unknown"

        # Extract Configuration from: - **Config**: Config(LLM=..., Data=..., Emb=..., Ret=..., Idx=..., Eval=...)
        config_match = re.search(r'- \*\*Config\*\*: Config\(LLM=(.*?), Data=(.*?), Emb=(.*?), Ret=(.*?), Idx=(.*?), Eval=(.*?)\)', exp)
        
        # metrics
        auc_match = re.search(r'- \*\*AUC\*\*: ([\d\.]+)', exp)
        recall_match = re.search(r'- \*\*Retrieval Recall\*\*: ([\d\.]+)', exp)
        
        if config_match and auc_match:
            data.append({
                'Timestamp': timestamp,
                'LLM': config_match.group(1),
                'Dataset': config_match.group(2),
                'Embedding': config_match.group(3),
                'Retriever': config_match.group(4),
                'Index Size': config_match.group(5),
                'Eval Samples': config_match.group(6),
                'AUC': float(auc_match.group(1)),
                'Retrieval Recall': float(recall_match.group(1)) if recall_match else 0.0
            })
    
    return pd.DataFrame(data)

def to_markdown_table(df):
    if df.empty:
        return ""
    # Create header
    headers = list(df.columns)
    header_row = "| " + " | ".join(headers) + " |"
    sep_row = "| " + " | ".join(["---"] * len(headers)) + " |"
    
    # Create rows
    rows = []
    for _, row in df.iterrows():
        # Format floats to 4 decimals
        formatted_row = []
        for val in row:
            if isinstance(val, float):
                formatted_row.append(f"{val:.4f}")
            else:
                formatted_row.append(str(val))
        rows.append("| " + " | ".join(formatted_row) + " |")
        
    return "\n".join([header_row, sep_row] + rows)

def generate_report(df, output_path):
    report_content = "# Experiment Results Analysis\n\n"
    
    # 1. Overall Summary
    best_run = df.loc[df['AUC'].idxmax()]
    report_content += "## 1. Overall Best Performance\n\n"
    report_content += f"The highest AUC achieving configuration was:\n"
    report_content += f"- **LLM**: `{best_run['LLM']}`\n"
    report_content += f"- **Embedding**: `{best_run['Embedding']}`\n"
    report_content += f"- **Retriever**: `{best_run['Retriever']}`\n"
    report_content += f"- **Dataset**: `{best_run['Dataset']}`\n"
    report_content += f"- **AUC**: **{best_run['AUC']:.4f}**\n\n"

    # 2. Performance by LLM
    report_content += "## 2. Performance by LLM\n\n"
    llm_stats = df.groupby('LLM')[['AUC', 'Retrieval Recall']].mean().reset_index().sort_values(by='AUC', ascending=False)
    report_content += to_markdown_table(llm_stats) + "\n\n"

    # 3. Performance by Embedding Model
    report_content += "## 3. Performance by Embedding Model\n\n"
    emb_stats = df.groupby('Embedding')[['AUC', 'Retrieval Recall']].mean().reset_index().sort_values(by='AUC', ascending=False)
    report_content += to_markdown_table(emb_stats) + "\n\n"

    # 4. Performance by Retriever
    report_content += "## 4. Performance by Retriever\n\n"
    ret_stats = df.groupby('Retriever')[['AUC', 'Retrieval Recall']].mean().reset_index().sort_values(by='AUC', ascending=False)
    report_content += to_markdown_table(ret_stats) + "\n\n"

    # 5. Dataset Difficulty
    report_content += "## 5. Dataset Difficulty (Average AUC)\n\n"
    data_stats = df.groupby('Dataset')[['AUC', 'Retrieval Recall']].mean().reset_index().sort_values(by='AUC', ascending=True)
    report_content += to_markdown_table(data_stats) + "\n\n"

    # 6. Full Data Table
    report_content += "## 6. All Experiment Runs\n\n"
    # Select key columns for cleaner table
    display_df = df[['Timestamp', 'LLM', 'Embedding', 'Dataset', 'Retriever', 'AUC', 'Retrieval Recall']]
    report_content += to_markdown_table(display_df.sort_values(by='AUC', ascending=False))
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"Report generated at {output_path}")

def main():
    print("Starting process_results.py...")
    if not os.path.exists(EXPERIMENT_FILE):
        print(f"Error: {EXPERIMENT_FILE} not found.")
        return

    print(f"Parsing {EXPERIMENT_FILE}...")
    df = parse_experiment_results(EXPERIMENT_FILE)
    
    if df.empty:
        print("No data extracted. Check regex or file format.")
        return

    # Save CSV
    df.to_csv(CSV_FILE, index=False)
    print(f"Extracted {len(df)} runs to {CSV_FILE}")

    # Generate Report
    print(f"Generating report to {REPORT_FILE}...")
    generate_report(df, REPORT_FILE)
    print("Done.")

if __name__ == "__main__":
    main()
