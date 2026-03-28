from __future__ import annotations

import random

from ..types import DatasetSplit, DocumentRecord
from .loaders import get_dataset_loader


def prepare_dataset_split(
    documents: list[DocumentRecord],
    index_size: int,
    eval_size: int,
    seed: int,
) -> DatasetSplit:
    shuffled = list(documents)
    random.Random(seed).shuffle(shuffled)
    required = index_size + eval_size
    if len(shuffled) < required:
        raise ValueError(f"Need at least {required} documents, found {len(shuffled)}")

    members = shuffled[:index_size]
    non_members = shuffled[index_size : index_size + eval_size]
    eval_members = random.Random(seed + 1).sample(members, min(len(members), eval_size))
    eval_non_members = non_members[:eval_size]
    return DatasetSplit(
        members=members,
        non_members=non_members,
        eval_members=eval_members,
        eval_non_members=eval_non_members,
    )


__all__ = ["get_dataset_loader", "prepare_dataset_split"]
