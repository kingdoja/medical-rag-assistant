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


class TestADTermRecognition:
    """Test suite for autonomous driving term recognition."""
    
    def test_sensor_term_detection(self):
        """Test detection of sensor-related terms."""
        analyzer = QueryAnalyzer()
        
        # Test Chinese sensor terms
        analysis = analyzer.analyze("摄像头的分辨率是多少？")
        assert "摄像头" in analysis.detected_terms
        assert "分辨率" in analysis.detected_terms
        assert analysis.term_types["摄像头"] == "sensor"
        assert analysis.term_types["分辨率"] == "sensor"
        
        # Test English sensor terms
        analysis2 = analyzer.analyze("What is the camera resolution?")
        assert "camera" in analysis2.detected_terms
        assert "resolution" in analysis2.detected_terms
        assert analysis2.term_types["camera"] == "sensor"
    
    def test_lidar_term_detection(self):
        """Test detection of LiDAR-related terms."""
        analyzer = QueryAnalyzer()
        
        # Test Chinese
        analysis = analyzer.analyze("激光雷达的探测距离是多少？")
        assert "激光雷达" in analysis.detected_terms
        assert "探测距离" in analysis.detected_terms
        assert analysis.term_types["激光雷达"] == "sensor"
        
        # Test English
        analysis2 = analyzer.analyze("What is the LiDAR detection range?")
        assert "lidar" in analysis2.detected_terms
        assert "detection range" in analysis2.detected_terms
    
    def test_radar_term_detection(self):
        """Test detection of radar-related terms."""
        analyzer = QueryAnalyzer()
        
        analysis = analyzer.analyze("毫米波雷达的视场角是多少？")
        assert "毫米波雷达" in analysis.detected_terms
        assert "视场角" in analysis.detected_terms
        assert analysis.term_types["毫米波雷达"] == "sensor"
    
    def test_algorithm_term_detection(self):
        """Test detection of algorithm-related terms."""
        analyzer = QueryAnalyzer()
        
        # Perception algorithm
        analysis = analyzer.analyze("目标检测算法的原理是什么？")
        assert "目标检测" in analysis.detected_terms
        assert analysis.term_types["目标检测"] == "algorithm"
        
        # Planning algorithm
        analysis2 = analyzer.analyze("路径规划算法如何实现？")
        assert "路径规划" in analysis2.detected_terms
        assert analysis2.term_types["路径规划"] == "algorithm"
        
        # Control algorithm
        analysis3 = analyzer.analyze("PID控制器的参数如何调优？")
        assert "pid" in analysis3.detected_terms
        assert analysis3.term_types["pid"] == "algorithm"
    
    def test_system_term_detection(self):
        """Test detection of system-related terms."""
        analyzer = QueryAnalyzer()
        
        # ADAS
        analysis = analyzer.analyze("ADAS系统包含哪些功能？")
        assert "adas" in analysis.detected_terms
        assert analysis.term_types["adas"] == "system"
        
        # ODD
        analysis2 = analyzer.analyze("ODD的定义是什么？")
        assert "odd" in analysis2.detected_terms
        assert analysis2.term_types["odd"] == "system"
        
        # V2X
        analysis3 = analyzer.analyze("V2X通信协议有哪些？")
        assert "v2x" in analysis3.detected_terms
        assert analysis3.term_types["v2x"] == "system"
    
    def test_regulation_term_detection(self):
        """Test detection of regulation-related terms."""
        analyzer = QueryAnalyzer()
        
        # GB/T standard
        analysis = analyzer.analyze("GB/T自动驾驶分级标准是什么？")
        assert "gb/t" in analysis.detected_terms
        assert analysis.term_types["gb/t"] == "regulation"
        
        # ISO 26262
        analysis2 = analyzer.analyze("ISO 26262功能安全标准的要求是什么？")
        assert "iso 26262" in analysis2.detected_terms
        assert "功能安全" in analysis2.detected_terms
        assert analysis2.term_types["iso 26262"] == "regulation"
    
    def test_mixed_language_query(self):
        """Test support for mixed Chinese-English queries."""
        analyzer = QueryAnalyzer()
        
        # Mixed query
        analysis = analyzer.analyze("LiDAR的探测距离是多少？")
        assert "lidar" in analysis.detected_terms
        assert "探测距离" in analysis.detected_terms
        
        # Another mixed query
        analysis2 = analyzer.analyze("Camera分辨率和帧率的关系")
        assert "camera" in analysis2.detected_terms
        assert "分辨率" in analysis2.detected_terms
        assert "帧率" in analysis2.detected_terms
    
    def test_synonym_mapping(self):
        """Test synonym mapping functionality."""
        analyzer = QueryAnalyzer()
        
        # Test LiDAR synonyms
        synonyms = analyzer.get_synonyms("激光雷达")
        assert "lidar" in synonyms
        
        synonyms2 = analyzer.get_synonyms("LiDAR")
        assert "激光雷达" in synonyms2
        
        # Test camera synonyms
        synonyms3 = analyzer.get_synonyms("摄像头")
        assert "camera" in synonyms3
        assert "相机" in synonyms3
        
        # Test radar synonyms
        synonyms4 = analyzer.get_synonyms("毫米波雷达")
        assert "radar" in synonyms4
        
        # Test ADAS synonyms
        synonyms5 = analyzer.get_synonyms("ADAS")
        assert "高级驾驶辅助系统" in synonyms5
    
    def test_multiple_term_types(self):
        """Test detection of multiple term types in one query."""
        analyzer = QueryAnalyzer()
        
        # Query with sensor and algorithm terms
        analysis = analyzer.analyze("摄像头的目标检测算法如何实现？")
        assert "摄像头" in analysis.detected_terms
        assert "目标检测" in analysis.detected_terms
        assert analysis.term_types["摄像头"] == "sensor"
        assert analysis.term_types["目标检测"] == "algorithm"
        
        # Query with system and regulation terms
        analysis2 = analyzer.analyze("ADAS系统需要符合ISO 26262标准吗？")
        assert "adas" in analysis2.detected_terms
        assert "iso 26262" in analysis2.detected_terms
        assert analysis2.term_types["adas"] == "system"
        assert analysis2.term_types["iso 26262"] == "regulation"
    
    def test_case_insensitive_detection(self):
        """Test that term detection is case-insensitive."""
        analyzer = QueryAnalyzer()
        
        # Test uppercase
        analysis = analyzer.analyze("LIDAR的性能如何？")
        assert "lidar" in analysis.detected_terms
        
        # Test mixed case
        analysis2 = analyzer.analyze("Camera和Radar的对比")
        assert "camera" in analysis2.detected_terms
        assert "radar" in analysis2.detected_terms
    
    def test_calibration_terms(self):
        """Test detection of calibration-related terms."""
        analyzer = QueryAnalyzer()
        
        analysis = analyzer.analyze("摄像头内参标定的步骤是什么？")
        assert "摄像头" in analysis.detected_terms
        assert "标定" in analysis.detected_terms
        assert analysis.term_types["标定"] == "sensor"
    
    def test_no_terms_detected(self):
        """Test queries with no AD terms."""
        analyzer = QueryAnalyzer()
        
        analysis = analyzer.analyze("今天天气怎么样？")
        assert len(analysis.detected_terms) == 0
        assert len(analysis.term_types) == 0
    
    def test_term_detection_with_complex_query(self):
        """Test term detection in complex queries."""
        analyzer = QueryAnalyzer()
        
        # Comparison query with multiple terms
        analysis = analyzer.analyze("激光雷达和毫米波雷达在感知算法中的应用有什么不同？")
        assert "激光雷达" in analysis.detected_terms
        assert "毫米波雷达" in analysis.detected_terms
        assert "感知" in analysis.detected_terms
        assert analysis.complexity == "comparison"
        assert len(analysis.detected_terms) >= 3
