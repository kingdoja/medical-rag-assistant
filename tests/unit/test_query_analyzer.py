"""Unit tests for QueryAnalyzer.

Tests query complexity detection and intent classification for Chinese medical queries.
"""

import pytest
from src.core.query_engine.query_analyzer import (
    QueryAnalyzer,
    QueryAnalysis,
    create_query_analyzer,
)


class TestQueryAnalyzer:
    """Test suite for QueryAnalyzer."""
    
    def test_simple_query(self):
        """Test detection of simple queries."""
        analyzer = QueryAnalyzer()
        
        # Simple retrieval query
        analysis = analyzer.analyze("WHO运输指南的主要内容是什么？")
        
        assert analysis.complexity == "simple"
        assert analysis.intent == "retrieval"
        assert analysis.requires_multi_doc is False
    
    def test_comparison_query(self):
        """Test detection of comparison queries."""
        analyzer = QueryAnalyzer()
        
        # Comparison query with "不同" keyword
        analysis = analyzer.analyze("WHO运输指南和质量管理指南有什么不同？")
        
        assert analysis.complexity == "comparison"
        assert analysis.intent == "retrieval"
        assert analysis.requires_multi_doc is True
        assert "不同" in analysis.detected_keywords
    
    def test_aggregation_query(self):
        """Test detection of aggregation queries."""
        analyzer = QueryAnalyzer()
        
        # Aggregation query with "哪些" keyword
        analysis = analyzer.analyze("哪些文档提到了样本管理？")
        
        assert analysis.complexity == "aggregation"
        assert analysis.intent == "retrieval"
        assert analysis.requires_multi_doc is True
        assert "哪些" in analysis.detected_keywords
    
    def test_multi_part_query_with_multiple_questions(self):
        """Test detection of multi-part queries with multiple question marks."""
        analyzer = QueryAnalyzer()
        
        # Multi-part query with multiple questions
        analysis = analyzer.analyze("什么是质量控制？如何实施？")
        
        assert analysis.complexity == "multi_part"
        assert analysis.intent == "retrieval"
        assert analysis.requires_multi_doc is True
        assert len(analysis.sub_queries) >= 2
    
    def test_multi_part_query_with_conjunctions(self):
        """Test detection of multi-part queries with conjunctions."""
        analyzer = QueryAnalyzer()
        
        # Multi-part query with "以及" conjunction
        analysis = analyzer.analyze("样本管理的流程以及注意事项以及质量要求")
        
        assert analysis.complexity == "multi_part"
        assert analysis.intent == "retrieval"
        assert analysis.requires_multi_doc is True
    
    def test_predictive_boundary_query(self):
        """Test detection of predictive boundary queries."""
        analyzer = QueryAnalyzer()
        
        # Predictive query
        analysis = analyzer.analyze("下个月最可能发生什么质量问题？")
        
        assert analysis.intent == "boundary"
        assert "下个月" in analysis.detected_keywords or "最可能" in analysis.detected_keywords
    
    def test_diagnostic_boundary_query(self):
        """Test detection of diagnostic boundary queries."""
        analyzer = QueryAnalyzer()
        
        # Diagnostic query
        analysis = analyzer.analyze("这个症状应该如何诊断？")
        
        assert analysis.intent == "boundary"
        assert "诊断" in analysis.detected_keywords
    
    def test_scope_inquiry_query(self):
        """Test detection of scope inquiry queries."""
        analyzer = QueryAnalyzer()
        
        # Scope inquiry query
        analysis = analyzer.analyze("知识库包含哪些文档？")
        
        assert analysis.intent == "scope_inquiry"
        assert analysis.requires_multi_doc is False
        assert "包含" in analysis.detected_keywords or "知识库" in analysis.detected_keywords
    
    def test_empty_query(self):
        """Test handling of empty queries."""
        analyzer = QueryAnalyzer()
        
        analysis = analyzer.analyze("")
        
        assert analysis.complexity == "simple"
        assert analysis.intent == "retrieval"
        assert analysis.requires_multi_doc is False
        assert len(analysis.detected_keywords) == 0
    
    def test_factory_function(self):
        """Test factory function creates valid analyzer."""
        analyzer = create_query_analyzer()
        
        assert isinstance(analyzer, QueryAnalyzer)
        
        # Verify it works
        analysis = analyzer.analyze("测试查询")
        assert isinstance(analysis, QueryAnalysis)
    
    def test_comparison_keywords_detection(self):
        """Test various comparison keywords are detected."""
        analyzer = QueryAnalyzer()
        
        comparison_queries = [
            "A和B的区别是什么？",
            "比较A和B",
            "A相比B有什么差异？",
            "A vs B",
        ]
        
        for query in comparison_queries:
            analysis = analyzer.analyze(query)
            assert analysis.complexity == "comparison", f"Failed for query: {query}"
            assert analysis.requires_multi_doc is True
    
    def test_aggregation_keywords_detection(self):
        """Test various aggregation keywords are detected."""
        analyzer = QueryAnalyzer()
        
        aggregation_queries = [
            "总结所有相关文档",
            "列举所有方法",
            "汇总全部信息",
        ]
        
        for query in aggregation_queries:
            analysis = analyzer.analyze(query)
            assert analysis.complexity == "aggregation", f"Failed for query: {query}"
            assert analysis.requires_multi_doc is True
    
    def test_sub_query_extraction(self):
        """Test extraction of sub-queries from multi-part queries."""
        analyzer = QueryAnalyzer()
        
        # Query with multiple question marks
        analysis = analyzer.analyze("什么是质量控制？如何实施？有什么标准？")
        
        assert analysis.complexity == "multi_part"
        assert len(analysis.sub_queries) == 3
        
        # Query with conjunctions
        analysis2 = analyzer.analyze("样本管理流程以及注意事项")
        
        assert analysis2.complexity == "multi_part"
        assert len(analysis2.sub_queries) >= 2
