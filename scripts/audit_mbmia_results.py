from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Iterable


CONTROL_COLUMNS = {
    "auc",
    "auc_ci_low",
    "auc_ci_high",
    "pr_auc",
    "tpr_at_5_fpr",
    "threshold_source",
    "calibration_member_samples",
    "calibration_non_member_samples",
    "chunk_chars",
    "eval_non_member_exact_duplicate_rate",
    "eval_non_member_near_duplicate_rate",
    "member_query_answer_leakage_rate",
    "non_member_query_answer_leakage_rate",
    "member_context_answer_coverage",
    "non_member_context_answer_coverage",
    "member_common_answer_rate",
}


def _resolve_input(path: Path) -> Path:
    if path.is_dir():
        return path / "summary.csv"
    return path


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _float(row: dict[str, str], key: str) -> float | None:
    value = row.get(key, "")
    if value in {"", "None", "nan", "NaN"}:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _float_any(row: dict[str, str], keys: list[str]) -> float | None:
    for key in keys:
        value = _float(row, key)
        if value is not None:
            return value
    return None


def _success_rows(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row.get("status", "success") == "success"]


def audit_rows(rows: list[dict[str, str]]) -> list[str]:
    messages: list[str] = []
    if not rows:
        return ["ERROR: no rows found"]

    columns = set(rows[0])
    missing = sorted(CONTROL_COLUMNS.difference(columns))
    if missing:
        messages.append(
            "ERROR: missing publication-control columns: " + ", ".join(missing)
        )

    success_rows = _success_rows(rows)
    if not success_rows:
        messages.append("ERROR: no successful rows found")
        return messages

    near_ceiling_labels: list[str] = []
    for index, row in enumerate(success_rows, start=1):
        label = row.get("run_name") or f"row {index}"
        auc = _float_any(row, ["auc", "AUC"])
        retrieval_recall = _float_any(row, ["retrieval_recall", "Retrieval Recall"])
        threshold_source = row.get("threshold_source", "")
        study_name = row.get("study_name", "")

        if threshold_source and threshold_source != "calibration" and study_name != "ablation_gamma":
            messages.append(f"WARNING: {label}: threshold_source={threshold_source!r} outside gamma study")

        if "calibration_member_samples" in columns and "calibration_non_member_samples" in columns:
            cal_members = _float(row, "calibration_member_samples")
            cal_non_members = _float(row, "calibration_non_member_samples")
            if cal_members == 0 or cal_non_members == 0:
                messages.append(f"WARNING: {label}: missing calibration samples")

        if "chunk_chars" in columns:
            chunk_chars = _float(row, "chunk_chars")
            if chunk_chars in {None, 0.0}:
                messages.append(f"WARNING: {label}: full-document indexing or missing chunk_chars")

        if "eval_non_member_exact_duplicate_rate" in columns:
            exact_dup = _float(row, "eval_non_member_exact_duplicate_rate")
            if exact_dup and exact_dup > 0:
                messages.append(f"ERROR: {label}: exact non-member duplicate rate is {exact_dup:.4f}")
        if "eval_non_member_near_duplicate_rate" in columns:
            near_dup = _float(row, "eval_non_member_near_duplicate_rate")
            if near_dup and near_dup > 0:
                messages.append(f"WARNING: {label}: near-duplicate non-member rate is {near_dup:.4f}")

        member_query_leakage = _float(row, "member_query_answer_leakage_rate")
        non_member_query_leakage = _float(row, "non_member_query_answer_leakage_rate")
        if member_query_leakage and member_query_leakage > 0:
            messages.append(f"ERROR: {label}: member masked-query answer leakage is {member_query_leakage:.4f}")
        if non_member_query_leakage and non_member_query_leakage > 0:
            messages.append(f"ERROR: {label}: non-member masked-query answer leakage is {non_member_query_leakage:.4f}")

        non_member_context_coverage = _float(row, "non_member_context_answer_coverage")
        if non_member_context_coverage and non_member_context_coverage > 0.10:
            messages.append(
                f"WARNING: {label}: non-member retrieved context contains masked answers "
                f"at rate {non_member_context_coverage:.4f}"
            )

        member_common_answer_rate = _float(row, "member_common_answer_rate")
        if member_common_answer_rate and member_common_answer_rate > 0.30:
            messages.append(f"WARNING: {label}: high common-answer mask rate ({member_common_answer_rate:.4f})")

        ci_low = _float(row, "auc_ci_low")
        ci_high = _float(row, "auc_ci_high")
        if auc is not None and "auc_ci_low" in columns and "auc_ci_high" in columns and (ci_low is None or ci_high is None):
            messages.append(f"WARNING: {label}: missing AUC confidence interval")

        low_fpr_tpr = _float(row, "tpr_at_5_fpr")
        member_context_coverage = _float(row, "member_context_answer_coverage")
        if auc is not None and auc >= 0.98 and retrieval_recall is not None and retrieval_recall >= 0.99:
            near_ceiling_labels.append(label)
        if (
            auc is not None
            and auc >= 0.98
            and member_context_coverage is not None
            and member_context_coverage >= 0.95
        ):
            messages.append(
                f"WARNING: {label}: near-ceiling AUC with near-complete answer coverage in retrieved context "
                f"({member_context_coverage:.4f})"
            )
        if auc is not None and auc >= 0.90 and low_fpr_tpr is not None and low_fpr_tpr < 0.10:
            messages.append(f"WARNING: {label}: high AUC but weak TPR at 5% FPR ({low_fpr_tpr:.4f})")

    if near_ceiling_labels:
        examples = ", ".join(near_ceiling_labels[:5])
        suffix = "" if len(near_ceiling_labels) <= 5 else f", plus {len(near_ceiling_labels) - 5} more"
        messages.append(
            f"WARNING: {len(near_ceiling_labels)} rows have near-ceiling AUC with near-perfect retrieval recall "
            f"({examples}{suffix}); interpret as protocol-specific unless controls and low-FPR behavior support the claim"
        )

    return messages


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit MBMIA result CSVs for publication controls.")
    parser.add_argument("input", nargs="?", default="experiment_data.csv", help="summary.csv, legacy CSV, or run directory")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when warnings or errors are found.")
    args = parser.parse_args(argv)

    input_path = _resolve_input(Path(args.input))
    if not input_path.exists():
        raise FileNotFoundError(f"Input not found: {input_path}")

    rows = _read_rows(input_path)
    messages = audit_rows(rows)
    if messages:
        print(f"Audited {len(rows)} rows from {input_path}")
        for message in messages:
            print(message)
        return 1 if args.strict or any(message.startswith("ERROR:") for message in messages) else 0

    print(f"Audited {len(rows)} rows from {input_path}: no MBMIA publication-control issues found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
