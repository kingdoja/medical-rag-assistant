"""Integration tests for P1 pipeline components.

Tests the integration of QueryAnalyzer, DocumentGrouper, and CitationEnhancer
with the existing HybridSearch and ResponseBuilder pipeline.
"""

import pytest

from src.core.query_engine.document_grouper import DocumentGrouper
from src.core.query_engine.fusion import RRFFusion
from src.core.query_engine.hybrid_search import HybridSearch
from src.core.query_engine.query_analyzer import QueryAnalyzer
from src.core.query_engine.query_processor import QueryProcessor
from src.core.response.citation_enhancer import CitationEnhancer
from src.core.response.response_builder import ResponseBuilder
from src.core.types import RetrievalResult


class TestPipelineIntegration:
    """Test integration of P1 components in the query pipeline."""
    
    def test_query_analyzer_integration(self):
        """Test that QueryAnalyzer integrates with HybridSearch."""
        analyzer = QueryAnalyzer()
        processor = QueryProcessor()
        
        # Create HybridSearch with analyzer
        hybrid = HybridSearch(
            query_processor=processor,
            query_analyzer=analyzer,
        )
        
        # Verify analyzer is set
        assert hybrid.query_analyzer is not None
        assert isinstance(hybrid.query_analyzer, QueryAnalyzer)
    
    def test_document_grouper_integration_with_fusion(self):
        """Test that DocumentGrouper integrates with RRFFusion."""
        grouper = DocumentGrouper()
        fusion = RRFFusion(k=60, document_grouper=grouper)
        
        # Verify grouper is set
        assert fusion.document_grouper is not None
        assert isinstance(fusion.document_grouper, DocumentGrouper)
        
        # Test fuse_with_document_grouping method exists
        assert hasattr(fusion, 'fuse_with_document_grouping')
    
    def test_citation_enhancer_integration_with_response_builder(self):
        """Test that CitationEnhancer integrates with ResponseBuilder."""
        enhancer = CitationEnhancer()
        builder = ResponseBuilder(citation_enhancer=enhancer)
        
        # Verify enhancer is set
        assert builder.citation_enhancer is not None
        assert isinstance(builder.citation_enhancer, CitationEnhancer)
    
    def test_full_pipeline_with_query_analysis(self):
        """Test full pipeline with query analysis."""
        # Create components
        analyzer = QueryAnalyzer()
        processor = QueryProcessor()
        
        # Create HybridSearch with analyzer
        hybrid = HybridSearch(
            query_processor=processor,
            query_analyzer=analyzer,
        )
        
        # Test comparison query
        query = "WHO运输指南和质量管理指南有什么不同？"
        analysis = analyzer.analyze(query)
        
        # Verify analysis
        assert analysis.complexity == "comparison"
        assert analysis.requires_multi_doc is True
        assert "不同" in analysis.detected_keywords
    
    def test_document_grouping_with_fusion(self):
        """Test document grouping functionality in fusion."""
        # Create sample results from different documents
        results_list1 = [
            RetrievalResult(
                chunk_id="doc1_c1",
                score=0.9,
                text="Content from doc1",
                metadata={"source_path": "guideline1.pdf", "doc_type": "guideline"}
            ),
            RetrievalResult(
                chunk_id="doc1_c2",
                score=0.85,
                text="More content from doc1",
                metadata={"source_path": "guideline1.pdf", "doc_type": "guideline"}
            ),
        ]
        
        results_list2 = [
            RetrievalResult(
                chunk_id="doc2_c1",
                score=0.88,
                text="Content from doc2",
                metadata={"source_path": "guideline2.pdf", "doc_type": "guideline"}
            ),
        ]
        
        # Create fusion with document grouper
        grouper = DocumentGrouper()
        fusion = RRFFusion(k=60, document_grouper=grouper)
        
        # Test fuse_with_document_grouping
        fused = fusion.fuse_with_document_grouping(
            ranking_lists=[results_list1, results_list2],
            top_k=10,
            top_k_per_doc=2,
            min_docs=2,
        )
        
        # Verify results
        assert len(fused) > 0
        
        # Check that we have results from multiple documents
        doc_names = set()
        for result in fused:
            source = result.metadata.get("source_path", "")
            if source:
                doc_names.add(source)
        
        assert len(doc_names) >= 2, "Should have results from at least 2 documents"
    
    def test_citation_enhancement(self):
        """Test citation enhancement functionality."""
        enhancer = CitationEnhancer()
        
        # Create sample result
        result = RetrievalResult(
            chunk_id="test_001",
            score=0.95,
            text="## 样本运输要求\n\n样本应在适当温度下运输。",
            metadata={
                "source_path": "demo-data/guidelines/guideline_transport_who_2024.pdf",
                "doc_type": "guideline",
                "page": 5,
            }
        )
        
        # Enhance citation
        citation = enhancer.enhance_citation(result)
        
        # Verify enhancement
        assert citation.document_name == "guideline_transport_who_2024.pdf"
        assert citation.document_type == "guideline"
        assert citation.authority_score == 1.0  # Guidelines have highest authority
        assert citation.page == 5
        assert citation.section == "样本运输要求"
        assert len(citation.excerpt) > 0
    
    def test_factory_creates_integrated_pipeline(self):
        """Test that factory function creates fully integrated pipeline."""
        from src.core.query_engine.hybrid_search import create_hybrid_search
        
        # Create using factory
        hybrid = create_hybrid_search()
        
        # Verify all P1 components are present
        assert hybrid.query_analyzer is not None
        assert isinstance(hybrid.query_analyzer, QueryAnalyzer)
        
        # Verify fusion has document grouper
        if hybrid.fusion is not None:
            assert hybrid.fusion.document_grouper is not None
            assert isinstance(hybrid.fusion.document_grouper, DocumentGrouper)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
