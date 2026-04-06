"""Integration tests for P1 pipeline routing.

Tests the complete pipeline routing based on query analysis:
- Simple queries -> standard response
- Comparison queries -> comparison response with multi-document grouping
- Aggregation queries -> aggregation response with multi-document grouping
- Scope queries -> scope response
"""

import pytest

from src.core.query_engine.document_grouper import DocumentGrouper
from src.core.query_engine.fusion import RRFFusion
from src.core.query_engine.hybrid_search import HybridSearch, create_hybrid_search
from src.core.query_engine.query_analyzer import QueryAnalyzer
from src.core.query_engine.query_processor import QueryProcessor
from src.core.query_engine.scope_provider import ScopeProvider
from src.core.response.citation_enhancer import CitationEnhancer
from src.core.response.response_builder import ResponseBuilder
from src.core.types import RetrievalResult


class TestPipelineRouting:
    """Test pipeline routing based on query analysis."""
    
    def test_simple_query_routing(self):
        """Test that simple queries use standard response."""
        # Create components
        analyzer = QueryAnalyzer()
        
        # Analyze simple query
        query = "如何配置 Azure OpenAI？"
        analysis = analyzer.analyze(query)
        
        # Verify routing decision
        assert analysis.complexity == "simple"
        assert analysis.intent == "retrieval"
        assert analysis.requires_multi_doc is False
    
    def test_comparison_query_routing(self):
        """Test that comparison queries are detected and routed correctly."""
        # Create components
        analyzer = QueryAnalyzer()
        
        # Analyze comparison query
        query = "WHO运输指南和质量管理指南有什么不同？"
        analysis = analyzer.analyze(query)
        
        # Verify routing decision
        assert analysis.complexity == "comparison"
        assert analysis.intent == "retrieval"
        assert analysis.requires_multi_doc is True
        assert "不同" in analysis.detected_keywords
    
    def test_aggregation_query_routing(self):
        """Test that aggregation queries are detected and routed correctly."""
        # Create components
        analyzer = QueryAnalyzer()
        
        # Analyze aggregation query (without "知识库" to avoid scope_inquiry detection)
        query = "有哪些关于样本运输的指南和SOP？"
        analysis = analyzer.analyze(query)
        
        # Verify routing decision
        assert analysis.complexity == "aggregation"
        assert analysis.intent == "retrieval"
        assert analysis.requires_multi_doc is True
        assert "哪些" in analysis.detected_keywords
    
    def test_scope_query_routing(self):
        """Test that scope queries are detected and routed correctly."""
        # Create components
        analyzer = QueryAnalyzer()
        
        # Analyze scope query
        query = "知识库里包含哪些类型的文档？"
        analysis = analyzer.analyze(query)
        
        # Verify routing decision
        assert analysis.intent == "scope_inquiry"
        assert "包含" in analysis.detected_keywords or "知识库" in analysis.detected_keywords
    
    def test_hybrid_search_with_query_analysis(self):
        """Test that HybridSearch performs query analysis."""
        # Create HybridSearch with analyzer
        hybrid = create_hybrid_search()
        
        # Verify analyzer is present
        assert hybrid.query_analyzer is not None
        
        # Test with comparison query (without actual retrieval)
        query = "WHO运输指南和质量管理指南有什么不同？"
        
        # The search would normally be called, but we're just testing
        # that the analyzer is integrated
        assert hybrid.query_analyzer.analyze(query).complexity == "comparison"
    
    def test_document_grouping_for_multi_doc_queries(self):
        """Test that multi-document queries trigger document grouping."""
        # Create sample results from different documents
        results = [
            RetrievalResult(
                chunk_id="doc1_c1",
                score=0.9,
                text="Content from guideline 1",
                metadata={"source_path": "guideline1.pdf", "doc_type": "guideline"}
            ),
            RetrievalResult(
                chunk_id="doc1_c2",
                score=0.85,
                text="More content from guideline 1",
                metadata={"source_path": "guideline1.pdf", "doc_type": "guideline"}
            ),
            RetrievalResult(
                chunk_id="doc2_c1",
                score=0.88,
                text="Content from guideline 2",
                metadata={"source_path": "guideline2.pdf", "doc_type": "guideline"}
            ),
            RetrievalResult(
                chunk_id="doc2_c2",
                score=0.82,
                text="More content from guideline 2",
                metadata={"source_path": "guideline2.pdf", "doc_type": "guideline"}
            ),
        ]
        
        # Group by document
        grouper = DocumentGrouper()
        grouped = grouper.group_by_document(results, top_k_per_doc=2)
        
        # Verify grouping
        assert len(grouped) == 2
        assert "guideline1.pdf" in grouped
        assert "guideline2.pdf" in grouped
        assert len(grouped["guideline1.pdf"]) == 2
        assert len(grouped["guideline2.pdf"]) == 2
        
        # Ensure diversity
        diverse = grouper.ensure_diversity(grouped, min_docs=2)
        assert len(diverse) >= 2
    
    def test_response_builder_routing(self):
        """Test that ResponseBuilder routes to correct response type."""
        # Create response builder
        builder = ResponseBuilder()
        
        # Create sample grouped chunks
        grouped_chunks = {
            "guideline1.pdf": [
                RetrievalResult(
                    chunk_id="doc1_c1",
                    score=0.9,
                    text="Content from guideline 1",
                    metadata={"source_path": "guideline1.pdf", "doc_type": "guideline", "page": 5}
                ),
            ],
            "guideline2.pdf": [
                RetrievalResult(
                    chunk_id="doc2_c1",
                    score=0.88,
                    text="Content from guideline 2",
                    metadata={"source_path": "guideline2.pdf", "doc_type": "guideline", "page": 3}
                ),
            ],
        }
        
        # Test comparison response
        query = "WHO运输指南和质量管理指南有什么不同？"
        response = builder.build_multi_document_response(
            query=query,
            grouped_chunks=grouped_chunks,
            response_type="comparison",
        )
        
        # Verify response
        assert "对比分析" in response.content
        assert response.metadata["response_type"] == "comparison"
        assert response.metadata["multi_document"] is True
        assert response.metadata["document_count"] == 2
        
        # Test aggregation response
        query = "知识库里有哪些关于样本运输的资料？"
        response = builder.build_multi_document_response(
            query=query,
            grouped_chunks=grouped_chunks,
            response_type="aggregation",
        )
        
        # Verify response
        assert "综合汇总" in response.content
        assert response.metadata["response_type"] == "aggregation"
        assert response.metadata["multi_document"] is True
    
    def test_scope_response_routing(self):
        """Test that scope queries route to scope response."""
        # Create response builder with mock scope provider
        from unittest.mock import Mock
        
        mock_scope_provider = Mock(spec=ScopeProvider)
        mock_scope_provider.get_collection_scope.return_value = Mock(
            collection="medical_demo_v01",
            document_count=10,
            document_types={"guideline", "sop", "manual"},
            last_updated=None,
        )
        mock_scope_provider.format_scope_response.return_value = "## 知识库范围\n\n包含 10 个文档"
        
        builder = ResponseBuilder()
        builder.set_scope_provider(mock_scope_provider)
        
        # Build scope response
        query = "知识库里包含哪些类型的文档？"
        response = builder.build_scope_response(query=query, collection="medical_demo_v01")
        
        # Verify response
        assert response.metadata["scope_query"] is True
        assert "知识库范围" in response.content
        mock_scope_provider.get_collection_scope.assert_called_once_with("medical_demo_v01")
    
    def test_performance_logging_integration(self):
        """Test that performance logging is integrated in the pipeline."""
        # Create HybridSearch
        hybrid = create_hybrid_search()
        
        # Verify that _log_performance_metrics method exists
        assert hasattr(hybrid, '_log_performance_metrics')
        
        # The method should be called when total_time > 5000ms
        # This is tested in the actual search flow


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
