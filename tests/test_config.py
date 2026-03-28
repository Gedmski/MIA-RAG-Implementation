from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mia_rag.config import expand_experiment_configs, load_experiment_spec


def test_load_experiment_spec_and_expand_smoke_config():
    spec = load_experiment_spec(ROOT / "configs" / "smoke.yaml")
    assert spec.paths.results_root == "results"
    assert len(spec.datasets) == 3
    healthcaremagic = next(dataset for dataset in spec.datasets if dataset.name == "healthcaremagic")
    arxiv = next(dataset for dataset in spec.datasets if dataset.name == "arxiv")
    assert healthcaremagic.loader_options["text_fields"] == ["text"]
    assert arxiv.loader_options["title_fields"] == ["Titles"]
    assert arxiv.loader_options["abstract_fields"] == ["Abstracts"]
    assert arxiv.loader_options["category_fields"] == ["Categories"]
    assert arxiv.category == "Computation and Language"
    configs = expand_experiment_configs(spec)
    assert len(configs) == 6
    first = configs[0]
    assert first.dataset_name in {"healthcaremagic", "fiqa", "arxiv"}
    assert first.num_masks in {3, 5}
    assert first.retriever_k in {1, 3}
