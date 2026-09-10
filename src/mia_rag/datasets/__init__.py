from __future__ import annotations

import random

from ..types import DatasetSplit, DocumentRecord
from .loaders import get_dataset_loader


def prepare_dataset_split(
    documents: list[DocumentRecord],
    index_size: int,
    eval_size: int,
    seed: int,
    calibration_size: int = 0,
) -> DatasetSplit:
    if index_size <= 0:
        raise ValueError("index_size must be positive")
    if eval_size <= 0:
        raise ValueError("eval_size must be positive")
    if calibration_size < 0:
        raise ValueError("calibration_size must be non-negative")
    if index_size < eval_size + calibration_size:
        raise ValueError(
            "index_size must be at least eval_size + calibration_size so member calibration "
            "and evaluation targets are disjoint."
        )

    shuffled = list(documents)
    random.Random(seed).shuffle(shuffled)
    required = index_size + eval_size + calibration_size
    if len(shuffled) < required:
        raise ValueError(f"Need at least {required} documents, found {len(shuffled)}")

    members = shuffled[:index_size]
    holdout = shuffled[index_size : index_size + eval_size + calibration_size]
    member_targets = random.Random(seed + 1).sample(members, eval_size + calibration_size)
    calibration_members = member_targets[:calibration_size]
    eval_members = member_targets[calibration_size:]
    calibration_non_members = holdout[:calibration_size]
    eval_non_members = holdout[calibration_size : calibration_size + eval_size]
    return DatasetSplit(
        members=members,
        non_members=holdout,
        eval_members=eval_members,
        eval_non_members=eval_non_members,
        calibration_members=calibration_members,
        calibration_non_members=calibration_non_members,
    )


__all__ = ["get_dataset_loader", "prepare_dataset_split"]
