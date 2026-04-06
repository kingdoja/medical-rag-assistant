"""Unit tests for HybridSearch device metadata boosting."""

from __future__ import annotations

from src.core.query_engine.hybrid_search import HybridSearch
from src.core.types import RetrievalResult


def test_extract_device_tokens_keeps_significant_model_terms() -> None:
    """Device/model-like tokens should be extracted from mixed queries."""
    hybrid = HybridSearch()

    tokens = hybrid._extract_device_tokens("HistoCore PELORIS 3 设备异常报警后标准处理步骤是什么？")

    assert "histocore" in tokens
    assert "peloris" in tokens


def test_device_metadata_boost_promotes_matching_manual() -> None:
    """Results whose source metadata matches device tokens should be promoted."""
    hybrid = HybridSearch()

    guideline_result = RetrievalResult(
        chunk_id="guideline_001",
        score=0.79,
        text="Generic equipment troubleshooting guidance.",
        metadata={
            "source_path": "demo-data/guidelines/guideline_lab_quality_management_system_who_2011.pdf",
            "title": "Troubleshooting",
        },
    )
    manual_result = RetrievalResult(
        chunk_id="manual_001",
        score=0.70,
        text="HistoCore PELORIS 3 alarm handling steps.",
        metadata={
            "source_path": "demo-data/manuals/manual_histocore_peloris3_user_manual_zh-cn.pdf",
            "title": "HistoCore PELORIS 3 User Manual",
        },
    )

    boosted = hybrid._apply_query_specific_boosts(
        [guideline_result, manual_result],
        "HistoCore PELORIS 3 设备异常报警后标准处理步骤是什么？",
    )

    assert boosted[0].chunk_id == "manual_001"
    assert boosted[0].metadata["query_metadata_boost"] > 0


def test_non_device_query_does_not_apply_metadata_boost() -> None:
    """Pure Chinese generic queries should keep original ordering."""
    hybrid = HybridSearch()

    first = RetrievalResult(
        chunk_id="result_001",
        score=0.82,
        text="First result",
        metadata={"source_path": "a.pdf", "title": "A"},
    )
    second = RetrievalResult(
        chunk_id="result_002",
        score=0.70,
        text="Second result",
        metadata={"source_path": "b.pdf", "title": "B"},
    )

    boosted = hybrid._apply_query_specific_boosts(
        [first, second],
        "设备异常报警后标准处理步骤是什么？",
    )

    assert [item.chunk_id for item in boosted] == ["result_001", "result_002"]
    assert "query_metadata_boost" not in boosted[0].metadata
