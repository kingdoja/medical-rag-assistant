"""Unit tests for CitationEnhancer.

This module tests the citation enhancement components for P1 multi-document
reasoning scenarios, including metadata extraction, authority scoring, and ranking.
"""

import pytest
from typing import List

from src.core.response.citation_enhancer import CitationEnhancer, EnhancedCitation
from src.core.types import RetrievalResult


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def citation_enhancer() -> CitationEnhancer:
    """Create CitationEnhancer instance."""
    return CitationEnhancer()


@pytest.fixture
def guideline_result() -> RetrievalResult:
    """Create a guideline document retrieval result."""
    return RetrievalResult(
        chunk_id="guideline_001",
        score=0.95,
        text="# 实验室质量管理体系\n\n本指南规定了医学实验室质量管理的基本要求和实施方法。",
        metadata={
            "source_path": "demo-data/guidelines/guideline_lab_quality_management_system_who_2011.pdf",
            "page": 5,
            "chunk_index": 0,
            "title": "质量管理体系",
            "doc_type": "guideline",
        },
    )


@pytest.fixture
def sop_result() -> RetrievalResult:
    """Create an SOP document retrieval result."""
    return RetrievalResult(
        chunk_id="sop_001",
        score=0.87,
        text="## 样本管理标准操作程序\n\n1. 样本接收\n2. 样本标识\n3. 样本存储",
        metadata={
            "source_path": "demo-data/sops/sop_sample_management_who_toolkit_module5.pdf",
            "page": 10,
            "chunk_index": 5,
            "title": "样本管理SOP",
        },
    )


@pytest.fixture
def manual_result() -> RetrievalResult:
    """Create a manual document retrieval result."""
    return RetrievalResult(
        chunk_id="manual_001",
        score=0.72,
        text="### 设备操作说明\n\n本手册介绍 HistoCore PELORIS 3 组织处理系统的操作方法。",
        metadata={
            "source_path": "demo-data/manuals/manual_histocore_peloris3_user_manual_zh-cn.pdf",
            "page": 15,
            "chunk_index": 2,
            "title": "用户手册",
        },
    )


@pytest.fixture
def training_result() -> RetrievalResult:
    """Create a training document retrieval result."""
    return RetrievalResult(
        chunk_id="training_001",
        score=0.68,
        text="第一章 质量控制培训\n\n质量控制是确保检测结果准确性的关键环节。",
        metadata={
            "source_path": "demo-data/training/training_quality_control_who_toolkit_module7.pdf",
            "page": 3,
            "chunk_index": 0,
            "title": "质量控制培训",
        },
    )


@pytest.fixture
def unknown_result() -> RetrievalResult:
    """Create an unknown document type retrieval result."""
    return RetrievalResult(
        chunk_id="unknown_001",
        score=0.55,
        text="这是一段没有明确文档类型的内容。",
        metadata={
            "source_path": "data/misc/document.txt",
            "chunk_index": 0,
        },
    )


@pytest.fixture
def mixed_results(
    guideline_result: RetrievalResult,
    sop_result: RetrievalResult,
    manual_result: RetrievalResult,
    training_result: RetrievalResult,
) -> List[RetrievalResult]:
    """Create a mixed list of retrieval results."""
    return [guideline_result, sop_result, manual_result, training_result]


# =============================================================================
# CitationEnhancer Tests
# =============================================================================

class TestCitationEnhancer:
    """Tests for CitationEnhancer class."""
    
    def test_enhance_guideline_citation(
        self,
        citation_enhancer: CitationEnhancer,
        guideline_result: RetrievalResult,
    ) -> None:
        """Test enhancing a guideline document citation."""
        citation = citation_enhancer.enhance_citation(guideline_result)
        
        assert citation.document_type == "guideline"
        assert citation.authority_score == 1.0
        assert citation.relevance_score == 0.95
        assert citation.page == 5
        assert citation.chunk_id == "guideline_001"
        assert "guideline_lab_quality_management_system_who_2011.pdf" in citation.document_name
        assert citation.section == "实验室质量管理体系"
        assert len(citation.excerpt) > 0
    
    def test_enhance_sop_citation(
        self,
        citation_enhancer: CitationEnhancer,
        sop_result: RetrievalResult,
    ) -> None:
        """Test enhancing an SOP document citation."""
        citation = citation_enhancer.enhance_citation(sop_result)
        
        assert citation.document_type == "sop"
        assert citation.authority_score == 0.8
        assert citation.relevance_score == 0.87
        assert citation.page == 10
        assert citation.section == "样本管理标准操作程序"
    
    def test_enhance_manual_citation(
        self,
        citation_enhancer: CitationEnhancer,
        manual_result: RetrievalResult,
    ) -> None:
        """Test enhancing a manual document citation."""
        citation = citation_enhancer.enhance_citation(manual_result)
        
        assert citation.document_type == "manual"
        assert citation.authority_score == 0.6
        assert citation.relevance_score == 0.72
        assert citation.page == 15
        assert citation.section == "设备操作说明"
    
    def test_enhance_training_citation(
        self,
        citation_enhancer: CitationEnhancer,
        training_result: RetrievalResult,
    ) -> None:
        """Test enhancing a training document citation."""
        citation = citation_enhancer.enhance_citation(training_result)
        
        assert citation.document_type == "training"
        assert citation.authority_score == 0.4
        assert citation.relevance_score == 0.68
        assert citation.page == 3
        assert citation.section == "质量控制培训"
    
    def test_enhance_unknown_citation(
        self,
        citation_enhancer: CitationEnhancer,
        unknown_result: RetrievalResult,
    ) -> None:
        """Test enhancing an unknown document type citation."""
        citation = citation_enhancer.enhance_citation(unknown_result)
        
        assert citation.document_type == "unknown"
        assert citation.authority_score == 0.3
        assert citation.relevance_score == 0.55
        assert citation.section is None  # No section header in text
    
    def test_document_name_extraction(
        self,
        citation_enhancer: CitationEnhancer,
    ) -> None:
        """Test document name extraction from various path formats."""
        # Unix path
        result1 = RetrievalResult(
            chunk_id="test_001",
            score=0.9,
            text="Test content",
            metadata={"source_path": "demo-data/guidelines/test.pdf"},
        )
        citation1 = citation_enhancer.enhance_citation(result1)
        assert citation1.document_name == "test.pdf"
        
        # Windows path
        result2 = RetrievalResult(
            chunk_id="test_002",
            score=0.9,
            text="Test content",
            metadata={"source_path": "demo-data\\manuals\\manual.pdf"},
        )
        citation2 = citation_enhancer.enhance_citation(result2)
        assert citation2.document_name == "manual.pdf"
        
        # No path separators
        result3 = RetrievalResult(
            chunk_id="test_003",
            score=0.9,
            text="Test content",
            metadata={"source_path": "document.txt"},
        )
        citation3 = citation_enhancer.enhance_citation(result3)
        assert citation3.document_name == "document.txt"
    
    def test_section_extraction_markdown_headers(
        self,
        citation_enhancer: CitationEnhancer,
    ) -> None:
        """Test section extraction from Markdown headers."""
        # H1 header
        result1 = RetrievalResult(
            chunk_id="test_001",
            score=0.9,
            text="# 第一章 概述\n\n内容...",
            metadata={"source_path": "test.pdf"},
        )
        citation1 = citation_enhancer.enhance_citation(result1)
        assert citation1.section == "第一章 概述"
        
        # H2 header
        result2 = RetrievalResult(
            chunk_id="test_002",
            score=0.9,
            text="## 1.1 背景介绍\n\n内容...",
            metadata={"source_path": "test.pdf"},
        )
        citation2 = citation_enhancer.enhance_citation(result2)
        assert citation2.section == "1.1 背景介绍"
        
        # H3 header
        result3 = RetrievalResult(
            chunk_id="test_003",
            score=0.9,
            text="### 操作步骤：\n\n1. 步骤一",
            metadata={"source_path": "test.pdf"},
        )
        citation3 = citation_enhancer.enhance_citation(result3)
        assert citation3.section == "操作步骤"
    
    def test_section_extraction_chinese_numbering(
        self,
        citation_enhancer: CitationEnhancer,
    ) -> None:
        """Test section extraction from Chinese numbering formats."""
        # Chapter format
        result1 = RetrievalResult(
            chunk_id="test_001",
            score=0.9,
            text="第一章 质量管理\n\n内容...",
            metadata={"source_path": "test.pdf"},
        )
        citation1 = citation_enhancer.enhance_citation(result1)
        assert citation1.section == "质量管理"
        
        # Section format
        result2 = RetrievalResult(
            chunk_id="test_002",
            score=0.9,
            text="第二节 样本处理\n\n内容...",
            metadata={"source_path": "test.pdf"},
        )
        citation2 = citation_enhancer.enhance_citation(result2)
        assert citation2.section == "样本处理"
    
    def test_page_extraction(
        self,
        citation_enhancer: CitationEnhancer,
    ) -> None:
        """Test page number extraction from metadata."""
        # Integer page
        result1 = RetrievalResult(
            chunk_id="test_001",
            score=0.9,
            text="Content",
            metadata={"source_path": "test.pdf", "page": 10},
        )
        citation1 = citation_enhancer.enhance_citation(result1)
        assert citation1.page == 10
        
        # String page (should convert)
        result2 = RetrievalResult(
            chunk_id="test_002",
            score=0.9,
            text="Content",
            metadata={"source_path": "test.pdf", "page": "15"},
        )
        citation2 = citation_enhancer.enhance_citation(result2)
        assert citation2.page == 15
        
        # page_num field
        result3 = RetrievalResult(
            chunk_id="test_003",
            score=0.9,
            text="Content",
            metadata={"source_path": "test.pdf", "page_num": 20},
        )
        citation3 = citation_enhancer.enhance_citation(result3)
        assert citation3.page == 20
        
        # No page
        result4 = RetrievalResult(
            chunk_id="test_004",
            score=0.9,
            text="Content",
            metadata={"source_path": "test.pdf"},
        )
        citation4 = citation_enhancer.enhance_citation(result4)
        assert citation4.page is None
    
    def test_excerpt_generation(
        self,
        citation_enhancer: CitationEnhancer,
    ) -> None:
        """Test excerpt generation and truncation."""
        # Short text (no truncation)
        result1 = RetrievalResult(
            chunk_id="test_001",
            score=0.9,
            text="这是一段简短的文本。",
            metadata={"source_path": "test.pdf"},
        )
        citation1 = citation_enhancer.enhance_citation(result1)
        assert citation1.excerpt == "这是一段简短的文本。"
        assert not citation1.excerpt.endswith("...")
        
        # Long text (should truncate)
        long_text = "这是一段非常长的文本，用于测试截断功能。" * 20
        result2 = RetrievalResult(
            chunk_id="test_002",
            score=0.9,
            text=long_text,
            metadata={"source_path": "test.pdf"},
        )
        citation2 = citation_enhancer.enhance_citation(result2)
        assert len(citation2.excerpt) <= 153  # 150 + "..."
        assert citation2.excerpt.endswith("...")
    
    def test_metadata_preservation(
        self,
        citation_enhancer: CitationEnhancer,
    ) -> None:
        """Test that selected metadata fields are preserved."""
        result = RetrievalResult(
            chunk_id="test_001",
            score=0.9,
            text="Content",
            metadata={
                "source_path": "test.pdf",
                "title": "Test Document",
                "chunk_index": 5,
                "extra_field": "should not be included",
            },
        )
        
        citation = citation_enhancer.enhance_citation(result)
        
        assert "title" in citation.metadata
        assert citation.metadata["title"] == "Test Document"
        assert "chunk_index" in citation.metadata
        assert citation.metadata["chunk_index"] == 5
        assert "source_path" in citation.metadata
        assert "extra_field" not in citation.metadata
    
    def test_to_dict_serialization(
        self,
        citation_enhancer: CitationEnhancer,
        guideline_result: RetrievalResult,
    ) -> None:
        """Test EnhancedCitation.to_dict() serialization."""
        citation = citation_enhancer.enhance_citation(guideline_result)
        citation_dict = citation.to_dict()
        
        assert citation_dict["document_type"] == "guideline"
        assert citation_dict["relevance_score"] == 0.95
        assert citation_dict["authority_score"] == 1.0
        assert citation_dict["page"] == 5
        assert "section" in citation_dict
        assert "excerpt" in citation_dict
        assert "chunk_id" in citation_dict
        assert "metadata" in citation_dict


class TestCitationRanking:
    """Tests for citation ranking functionality."""
    
    def test_rank_by_relevance_score(
        self,
        citation_enhancer: CitationEnhancer,
        mixed_results: List[RetrievalResult],
    ) -> None:
        """Test that citations are ranked by relevance score (primary)."""
        citations = [
            citation_enhancer.enhance_citation(result)
            for result in mixed_results
        ]
        
        ranked = citation_enhancer.rank_citations(citations)
        
        # Should be sorted by relevance score descending
        assert ranked[0].relevance_score == 0.95  # guideline
        assert ranked[1].relevance_score == 0.87  # sop
        assert ranked[2].relevance_score == 0.72  # manual
        assert ranked[3].relevance_score == 0.68  # training
    
    def test_rank_by_authority_when_relevance_equal(
        self,
        citation_enhancer: CitationEnhancer,
    ) -> None:
        """Test that authority score is used as tie-breaker."""
        # Create results with same relevance but different types
        results = [
            RetrievalResult(
                chunk_id="training_001",
                score=0.80,
                text="Training content",
                metadata={"source_path": "training.pdf"},
            ),
            RetrievalResult(
                chunk_id="guideline_001",
                score=0.80,
                text="# Guideline content",
                metadata={"source_path": "guideline.pdf"},
            ),
            RetrievalResult(
                chunk_id="manual_001",
                score=0.80,
                text="Manual content",
                metadata={"source_path": "manual.pdf"},
            ),
        ]
        
        citations = [
            citation_enhancer.enhance_citation(result)
            for result in results
        ]
        
        ranked = citation_enhancer.rank_citations(citations)
        
        # With equal relevance, should rank by authority
        assert ranked[0].document_type == "guideline"  # authority 1.0
        assert ranked[1].document_type == "manual"  # authority 0.6
        assert ranked[2].document_type == "training"  # authority 0.4
    
    def test_rank_stability_with_document_name(
        self,
        citation_enhancer: CitationEnhancer,
    ) -> None:
        """Test that document name provides stable sorting."""
        # Create results with same relevance and authority
        results = [
            RetrievalResult(
                chunk_id="doc_z",
                score=0.80,
                text="Content",
                metadata={"source_path": "z_document.pdf"},
            ),
            RetrievalResult(
                chunk_id="doc_a",
                score=0.80,
                text="Content",
                metadata={"source_path": "a_document.pdf"},
            ),
            RetrievalResult(
                chunk_id="doc_m",
                score=0.80,
                text="Content",
                metadata={"source_path": "m_document.pdf"},
            ),
        ]
        
        citations = [
            citation_enhancer.enhance_citation(result)
            for result in results
        ]
        
        ranked = citation_enhancer.rank_citations(citations)
        
        # Should be alphabetically sorted by document name
        assert ranked[0].document_name == "a_document.pdf"
        assert ranked[1].document_name == "m_document.pdf"
        assert ranked[2].document_name == "z_document.pdf"


class TestCitationFormatting:
    """Tests for citation formatting functionality."""
    
    def test_format_inline_style(
        self,
        citation_enhancer: CitationEnhancer,
        guideline_result: RetrievalResult,
    ) -> None:
        """Test inline citation formatting."""
        citation = citation_enhancer.enhance_citation(guideline_result)
        formatted = citation_enhancer.format_citation(citation, index=1, style="inline")
        
        assert formatted == "[1]"
    
    def test_format_reference_style(
        self,
        citation_enhancer: CitationEnhancer,
        guideline_result: RetrievalResult,
    ) -> None:
        """Test reference list citation formatting."""
        citation = citation_enhancer.enhance_citation(guideline_result)
        formatted = citation_enhancer.format_citation(citation, index=1, style="reference")
        
        assert "[1]" in formatted
        assert "guideline_lab_quality_management_system_who_2011.pdf" in formatted
        assert "(p.5)" in formatted
    
    def test_format_reference_style_without_page(
        self,
        citation_enhancer: CitationEnhancer,
    ) -> None:
        """Test reference formatting when page is not available."""
        result = RetrievalResult(
            chunk_id="test_001",
            score=0.9,
            text="Content",
            metadata={"source_path": "test.pdf"},
        )
        citation = citation_enhancer.enhance_citation(result)
        formatted = citation_enhancer.format_citation(citation, index=2, style="reference")
        
        assert "[2]" in formatted
        assert "test.pdf" in formatted
        assert "(p." not in formatted
    
    def test_format_detailed_style(
        self,
        citation_enhancer: CitationEnhancer,
        guideline_result: RetrievalResult,
    ) -> None:
        """Test detailed citation formatting."""
        citation = citation_enhancer.enhance_citation(guideline_result)
        formatted = citation_enhancer.format_citation(citation, index=1, style="detailed")
        
        assert "[1]" in formatted
        assert "guideline_lab_quality_management_system_who_2011.pdf" in formatted
        assert "类型: guideline" in formatted
        assert "相关度:" in formatted
        assert "章节:" in formatted
        assert "页码: 5" in formatted
        assert "摘录:" in formatted
    
    def test_format_invalid_style(
        self,
        citation_enhancer: CitationEnhancer,
        guideline_result: RetrievalResult,
    ) -> None:
        """Test that invalid style raises ValueError."""
        citation = citation_enhancer.enhance_citation(guideline_result)
        
        with pytest.raises(ValueError, match="Unknown citation style"):
            citation_enhancer.format_citation(citation, index=1, style="invalid")


class TestDocumentTypeClassification:
    """Tests for document type classification logic."""
    
    def test_classify_by_explicit_metadata(
        self,
        citation_enhancer: CitationEnhancer,
    ) -> None:
        """Test classification using explicit doc_type metadata."""
        result = RetrievalResult(
            chunk_id="test_001",
            score=0.9,
            text="Content",
            metadata={
                "source_path": "random_name.pdf",
                "doc_type": "guideline",
            },
        )
        
        citation = citation_enhancer.enhance_citation(result)
        assert citation.document_type == "guideline"
    
    def test_classify_guideline_by_pattern(
        self,
        citation_enhancer: CitationEnhancer,
    ) -> None:
        """Test guideline classification by filename pattern."""
        patterns = [
            "guideline_lab_quality.pdf",
            "质量管理指南.pdf",
            "who_guideline_2024.pdf",
            "标准规范文件.pdf",
        ]
        
        for pattern in patterns:
            result = RetrievalResult(
                chunk_id="test",
                score=0.9,
                text="Content",
                metadata={"source_path": pattern},
            )
            citation = citation_enhancer.enhance_citation(result)
            assert citation.document_type == "guideline", f"Failed for: {pattern}"
    
    def test_classify_sop_by_pattern(
        self,
        citation_enhancer: CitationEnhancer,
    ) -> None:
        """Test SOP classification by filename pattern."""
        patterns = [
            "sop_sample_management.pdf",
            "标准操作程序_样本.pdf",
            "操作规程文件.pdf",
        ]
        
        for pattern in patterns:
            result = RetrievalResult(
                chunk_id="test",
                score=0.9,
                text="Content",
                metadata={"source_path": pattern},
            )
            citation = citation_enhancer.enhance_citation(result)
            assert citation.document_type == "sop", f"Failed for: {pattern}"
    
    def test_classify_manual_by_pattern(
        self,
        citation_enhancer: CitationEnhancer,
    ) -> None:
        """Test manual classification by filename pattern."""
        patterns = [
            "manual_histocore.pdf",
            "用户手册.pdf",
            "user_manual_device.pdf",
            "操作手册.pdf",
        ]
        
        for pattern in patterns:
            result = RetrievalResult(
                chunk_id="test",
                score=0.9,
                text="Content",
                metadata={"source_path": pattern},
            )
            citation = citation_enhancer.enhance_citation(result)
            assert citation.document_type == "manual", f"Failed for: {pattern}"
    
    def test_classify_training_by_pattern(
        self,
        citation_enhancer: CitationEnhancer,
    ) -> None:
        """Test training classification by filename pattern."""
        patterns = [
            "training_quality_control.pdf",
            "培训材料.pdf",
            "教程文档.pdf",
        ]
        
        for pattern in patterns:
            result = RetrievalResult(
                chunk_id="test",
                score=0.9,
                text="Content",
                metadata={"source_path": pattern},
            )
            citation = citation_enhancer.enhance_citation(result)
            assert citation.document_type == "training", f"Failed for: {pattern}"
