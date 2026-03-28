from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DocumentRecord:
    doc_id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DatasetSplit:
    members: list[DocumentRecord]
    non_members: list[DocumentRecord]
    eval_members: list[DocumentRecord]
    eval_non_members: list[DocumentRecord]
