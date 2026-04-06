"""Unit tests for ResponseBuilder multi-document synthesis functionality.

Tests the enhanced ResponseBuilder methods for comparison, aggregation,
and standard multi-document responses.
"""

import pytest

from src.core.response.response_builder import ResponseBuilder
from src.core.types import RetrievalResult


@pytest.fixture
def sample_grouped_chunks():
    """Create sample grouped chunks for testing."""
    return {
        "guideline_transport_who_2024.pdf": [
            RetrievalResult(
                chunk_id="doc1_chunk1",
                score=0.92,
                text="WHO运输指南规定：感染性物质必须使用三层包装系统。第一层为防漏容器，第二层为防水包装，第三层为外包装箱。",
                metadata={
                    "source_path": "demo-data/guidelines/guideline_transport_who_2024.pdf",
                    "page": 15,
                    "chunk_index": 5,
                }
            ),
            RetrievalResult(
                chunk_id="doc1_chunk2",
                score=0.88,
                text="运输温度要求：生物样本应在2-8°C冷链条件下运输，运输时间不超过24小时。",
                metadata={
                    "source_path": "demo-data/guidelines/guideline_transport_who_2024.pdf",
                    "page": 18,
                    "chunk_index": 7,
                }
            ),
        ],
        "guideline_quality_management_who_2011.pdf": [
            RetrievalResult(
                chunk_id="doc2_chunk1",
                score=0.85,
                text="质量管理指南要求：样本运输过程必须有完整的记录链，包括交接时间、温度监控和责任人签字。",
                metadata={
                    "source_path": "demo-data/guidelines/guideline_quality_management_who_2011.pdf",
                    "page": 42,
                    "chunk_index": 12,
                }
            ),
        ],
        "sop_sample_management_module5.pdf": [
            RetrievalResult(
                chunk_id="doc3_chunk1",
                score=0.80,
                text="SOP规定：样本运输前必须完成标签核对、包装检查和运输记录填写三个步骤。",
                metadata={
                    "source_path": "demo-data/sops/sop_sample_management_module5.pdf",
                    "page": 8,
                    "chunk_index": 3,
                }
            ),
        ],
    }


def test_build_comparison_response(sample_grouped_chunks):
    """Test comparison response formatting with clear attribution."""
    builder = ResponseBuilder()
    
    response = builder.build_multi_document_response(
        query="WHO运输指南和质量管理指南有什么不同？",
        grouped_chunks=sample_grouped_chunks,
        response_type="comparison",
    )
    
    # Verify response structure
    assert not response.is_empty
    assert "对比分析" in response.content
    assert "根据" in response.content
    
    # Verify document attribution
    assert "guideline_transport_who_2024.pdf" in response.content
    assert "guideline_quality_management_who_2011.pdf" in response.content
    
    # Verify citations are present
    assert len(response.citations) >= 2
    assert response.citations[0].index == 1
    
    # Verify metadata
    assert response.metadata["response_type"] == "comparison"
    assert response.metadata["multi_document"] is True
    assert response.metadata["document_count"] == 3


def test_build_aggregation_response(sample_grouped_chunks):
    """Test aggregation response with numbered points and citations."""
    builder = ResponseBuilder()
    
    response = builder.build_multi_document_response(
        query="样本运输有哪些要求？",
        grouped_chunks=sample_grouped_chunks,
        response_type="aggregation",
    )
    
    # Verify response structure
    assert not response.is_empty
    assert "综合汇总" in response.content
    assert "来源:" in response.content
    
    # Verify numbered points (at least 2 points from different docs)
    assert "1." in response.content
    assert "2." in response.content
    
    # Verify citations are included
    assert len(response.citations) >= 2
    
    # Verify metadata
    assert response.metadata["response_type"] == "aggregation"
    assert response.metadata["multi_document"] is True


def test_build_standard_multi_doc_response(sample_grouped_chunks):
    """Test standard multi-document response with coherent synthesis."""
    builder = ResponseBuilder()
    
    response = builder.build_multi_document_response(
        query="样本运输的规范要求",
        grouped_chunks=sample_grouped_chunks,
        response_type="standard",
    )
    
    # Verify response structure
    assert not response.is_empty
    assert "检索结果" in response.content
    assert "个文档" in response.content
    
    # Verify document information is present
    assert "guideline_transport_who_2024.pdf" in response.content
    
    # Verify citations section
    assert "引用来源" in response.content
    assert len(response.citations) >= 2
    
    # Verify metadata
    assert response.metadata["response_type"] == "standard"
    assert response.metadata["multi_document"] is True


def test_empty_grouped_chunks():
    """Test handling of empty grouped chunks."""
    builder = ResponseBuilder()
    
    response = builder.build_multi_document_response(
        query="测试查询",
        grouped_chunks={},
        response_type="standard",
    )
    
    # Should return empty response
    assert response.is_empty
    assert "未找到相关结果" in response.content


def test_citation_enhancement_integration(sample_grouped_chunks):
    """Test that citation enhancer is properly integrated."""
    builder = ResponseBuilder()
    
    response = builder.build_multi_document_response(
        query="样本运输要求",
        grouped_chunks=sample_grouped_chunks,
        response_type="standard",
    )
    
    # Verify enhanced citation metadata
    assert len(response.citations) > 0
    
    # Check that citations have required fields
    for citation in response.citations:
        assert citation.source is not None
        assert citation.score >= 0
        assert citation.index > 0
    
    # Verify citations are ranked by relevance
    scores = [c.score for c in response.citations]
    assert scores == sorted(scores, reverse=True)


def test_document_type_translation():
    """Test document type translation to Chinese."""
    builder = ResponseBuilder()
    
    # Test various document types
    assert builder._translate_doc_type("guideline") == "指南"
    assert builder._translate_doc_type("sop") == "SOP"
    assert builder._translate_doc_type("manual") == "说明书"
    assert builder._translate_doc_type("training") == "培训材料"
    assert builder._translate_doc_type("unknown") == "其他"


def test_comparison_with_single_document():
    """Test comparison response with only one document."""
    builder = ResponseBuilder()
    
    single_doc_chunks = {
        "guideline_transport_who_2024.pdf": [
            RetrievalResult(
                chunk_id="doc1_chunk1",
                score=0.92,
                text="WHO运输指南规定：感染性物质必须使用三层包装系统。",
                metadata={
                    "source_path": "demo-data/guidelines/guideline_transport_who_2024.pdf",
                    "page": 15,
                }
            ),
        ],
    }
    
    response = builder.build_multi_document_response(
        query="运输要求是什么？",
        grouped_chunks=single_doc_chunks,
        response_type="comparison",
    )
    
    # Should still work with single document
    assert not response.is_empty
    assert "对比分析" in response.content
    assert len(response.citations) == 1


def test_aggregation_respects_limit():
    """Test that aggregation response limits number of points."""
    builder = ResponseBuilder()
    
    # Create many documents
    many_docs = {}
    for i in range(10):
        doc_name = f"document_{i}.pdf"
        many_docs[doc_name] = [
            RetrievalResult(
                chunk_id=f"doc{i}_chunk1",
                score=0.9 - (i * 0.05),
                text=f"内容 {i}：这是第 {i} 个文档的内容。",
                metadata={
                    "source_path": f"data/{doc_name}",
                    "page": 1,
                }
            ),
        ]
    
    response = builder.build_multi_document_response(
        query="汇总所有文档",
        grouped_chunks=many_docs,
        response_type="aggregation",
    )
    
    # Should limit to 5 points
    content_lines = response.content.split("\n")
    numbered_points = [line for line in content_lines if line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "6."))]
    
    # Should have at most 5 numbered points
    assert len([p for p in numbered_points if p.strip().startswith(("1.", "2.", "3.", "4.", "5."))]) <= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
