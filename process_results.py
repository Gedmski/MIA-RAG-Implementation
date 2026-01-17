import re
import pandas as pd
import os

EXPERIMENT_FILE = 'experiment_results.md'
CSV_FILE = 'experiment_data.csv'
REPORT_FILE = 'results_report.md'

def parse_experiment_results(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by experiment runs
    experiments = content.split('## Experiment Run: ')
    data = []

    for exp in experiments:
        if not exp.strip():
            continue

        # Extract timestamp
        timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', exp)
        timestamp = timestamp_match.group(1) if timestamp_match else "Unknown"

        # Extract Configuration
        llm = re.search(r'- \*\*LLM\*\*: `(.*?)`', exp)
        embedding = re.search(r'- \*\*Embedding\*\*: `(.*?)`', exp)
        dataset = re.search(r'- \*\*Dataset\*\*: `(.*?)`', exp)
        retriever = re.search(r'- \*\*Retriever\*\*: `(.*?)`', exp)

        # Extract Metrics
        auc = re.search(r'\| \*\*AUC\*\* \| \*\*(.*?)\*\* \|', exp)
        accuracy = re.search(r'\| Accuracy \| (.*?) \|', exp)
        precision = re.search(r'\| Precision \| (.*?) \|', exp)
        recall = re.search(r'\| Recall \| (.*?) \|', exp)
        f1 = re.search(r'\| F1 Score \| (.*?) \|', exp)

        if llm and auc:
            data.append({
                'Timestamp': timestamp,
                'LLM': llm.group(1),
                'Embedding': embedding.group(1) if embedding else "Unknown",
                'Dataset': dataset.group(1) if dataset else "Unknown",
                'Retriever': retriever.group(1) if retriever else "Unknown",
                'AUC': float(auc.group(1)),
                'Accuracy': float(accuracy.group(1)) if accuracy else 0.0,
                'Precision': float(precision.group(1)) if precision else 0.0,
                'Recall': float(recall.group(1)) if recall else 0.0,
                'F1 Score': float(f1.group(1)) if f1 else 0.0
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
    llm_stats = df.groupby('LLM')[['AUC', 'Accuracy']].mean().reset_index().sort_values(by='AUC', ascending=False)
    report_content += to_markdown_table(llm_stats) + "\n\n"

    # 3. Performance by Emebdding
    report_content += "## 3. Performance by Embedding Model\n\n"
    emb_stats = df.groupby('Embedding')[['AUC', 'Accuracy']].mean().reset_index().sort_values(by='AUC', ascending=False)
    report_content += to_markdown_table(emb_stats) + "\n\n"

    # 4. Performance by Retriever
    report_content += "## 4. Performance by Retriever\n\n"
    ret_stats = df.groupby('Retriever')[['AUC', 'Accuracy']].mean().reset_index().sort_values(by='AUC', ascending=False)
    report_content += to_markdown_table(ret_stats) + "\n\n"

    # 5. Dataset Difficulty
    report_content += "## 5. Dataset Difficulty (Average AUC)\n\n"
    data_stats = df.groupby('Dataset')[['AUC', 'Accuracy']].mean().reset_index().sort_values(by='AUC', ascending=True)
    report_content += to_markdown_table(data_stats) + "\n\n"

    # 6. Full Data Table
    report_content += "## 6. All Experiment Runs\n\n"
    # Select key columns for cleaner table
    display_df = df[['Timestamp', 'LLM', 'Embedding', 'Dataset', 'Retriever', 'AUC', 'Accuracy']]
    report_content += to_markdown_table(display_df.sort_values(by='AUC', ascending=False))
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"Report generated at {output_path}")

def main():
    if not os.path.exists(EXPERIMENT_FILE):
        print(f"Error: {EXPERIMENT_FILE} not found.")
        return

    df = parse_experiment_results(EXPERIMENT_FILE)
    
    if df.empty:
        print("No data extracted. Check regex or file format.")
        return

    # Save CSV
    df.to_csv(CSV_FILE, index=False)
    print(f"Extracted {len(df)} runs to {CSV_FILE}")

    # Generate Report
    generate_report(df, REPORT_FILE)

if __name__ == "__main__":
    main()
