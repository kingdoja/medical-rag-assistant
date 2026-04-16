"""Unit tests for BoundaryValidator adapted for Autonomous Driving domain.

This module tests the boundary validation functionality for the autonomous
driving knowledge retrieval system, including:
- Predictive query detection and refusal
- Real-time diagnostic query detection and refusal
- Low relevance acknowledgment
- Boundary refusal logging
"""

import pytest
from typing import List

from src.core.response.response_builder import ResponseBuilder, BoundaryCheck
from src.core.types import RetrievalResult


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def response_builder() -> ResponseBuilder:
    """Create ResponseBuilder instance for testing."""
    return ResponseBuilder()


@pytest.fixture
def sample_ad_results() -> List[RetrievalResult]:
    """Create sample autonomous driving retrieval results."""
    return [
        RetrievalResult(
            chunk_id="sensor_doc_001",
            score=0.85,
            text="激光雷达（LiDAR）是一种主动式传感器，通过发射激光束并测量反射时间来获取距离信息。"
            "典型的车载激光雷达探测距离可达200米，角分辨率为0.1°。",
            metadata={
                "source_path": "docs/sensors/lidar_spec.pdf",
                "page": 5,
                "doc_type": "sensor_doc",
                "sensor_type": "lidar",
            },
        ),
        RetrievalResult(
            chunk_id="algorithm_doc_001",
            score=0.78,
            text="目标检测算法是感知模块的核心组件，负责识别和定位道路上的车辆、行人和障碍物。"
            "常用的算法包括YOLO、Faster R-CNN等深度学习模型。",
            metadata={
                "source_path": "docs/algorithms/perception_design.pdf",
                "page": 12,
                "doc_type": "algorithm_doc",
                "algorithm_type": "perception",
            },
        ),
    ]


@pytest.fixture
def low_relevance_results() -> List[RetrievalResult]:
    """Create low-relevance retrieval results."""
    return [
        RetrievalResult(
            chunk_id="test_001",
            score=0.15,  # Below 0.3 threshold
            text="Irrelevant content for testing",
            metadata={"source_path": "docs/test.pdf"},
        )
    ]


# =============================================================================
# Predictive Query Detection Tests
# =============================================================================

class TestPredictiveQueryDetection:
    """Tests for predictive query pattern detection."""
    
    def test_detect_predictive_chinese_patterns(
        self,
        response_builder: ResponseBuilder,
    ) -> None:
        """Test detection of Chinese predictive patterns."""
        predictive_queries = [
            "预测下一代激光雷达的性能",
            "未来趋势是什么",
            "自动驾驶技术的发展方向",
            "预计明年会有什么新技术",
            "预期传感器成本会下降吗",
        ]
        
        for query in predictive_queries:
            check = response_builder.validate_query(query)
            assert check.is_valid is False, f"Query should be invalid: {query}"
            assert check.boundary_type == "predictive"
            assert check.detected_pattern is not None
            assert check.confidence > 0.8
    
    def test_detect_predictive_english_patterns(
        self,
        response_builder: ResponseBuilder,
    ) -> None:
        """Test detection of English predictive patterns."""
        predictive_queries = [
            "predict next generation lidar performance",
            "what is the future trend",
            "forecast sensor development",
        ]
        
        for query in predictive_queries:
            check = response_builder.validate_query(query)
            assert check.is_valid is False
            assert check.boundary_type == "predictive"
    
    def test_predictive_refusal_message_ad_domain(
        self,
        response_builder: ResponseBuilder,
    ) -> None:
        """Test that AD-specific refusal message is generated."""
        query = "预测下一代激光雷达的性能"
        check = response_builder.validate_query(query)
        
        assert check.refusal_message is not None
        assert "自动驾驶知识检索系统" in check.refusal_message
        assert "事实性信息检索" in check.refusal_message
        assert "预测" in check.refusal_message
    
    def test_predictive_alternatives_provided(
        self,
        response_builder: ResponseBuilder,
    ) -> None:
        """Test that alternative suggestions are provided for predictive queries."""
        query = "预测未来传感器趋势"
        check = response_builder.validate_query(query)
        
        assert len(check.suggested_alternatives) > 0
        # Should suggest querying existing technology
        alternatives_text = " ".join(check.suggested_alternatives)
        assert any(keyword in alternatives_text for keyword in ["当前", "已有", "标准"])


# =============================================================================
# Diagnostic Query Detection Tests
# =============================================================================

class TestDiagnosticQueryDetection:
    """Tests for real-time diagnostic query pattern detection."""
    
    def test_detect_diagnostic_chinese_patterns(
        self,
        response_builder: ResponseBuilder,
    ) -> None:
        """Test detection of Chinese diagnostic patterns."""
        diagnostic_queries = [
            "判断当前故障原因",
            "分析实时数据异常",
            "诊断传感器问题",
            "是否故障了",
            "摄像头出了什么问题",
            "如何修复这个故障",
        ]
        
        for query in diagnostic_queries:
            check = response_builder.validate_query(query)
            assert check.is_valid is False, f"Query should be invalid: {query}"
            assert check.boundary_type == "diagnostic"
            assert check.detected_pattern is not None
    
    def test_detect_diagnostic_english_patterns(
        self,
        response_builder: ResponseBuilder,
    ) -> None:
        """Test detection of English diagnostic patterns."""
        diagnostic_queries = [
            "diagnose current fault",
            "analyze real-time data",
            "is it faulty",
        ]
        
        for query in diagnostic_queries:
            check = response_builder.validate_query(query)
            assert check.is_valid is False
            assert check.boundary_type == "diagnostic"
    
    def test_diagnostic_refusal_message_ad_domain(
        self,
        response_builder: ResponseBuilder,
    ) -> None:
        """Test that AD-specific diagnostic refusal message is generated."""
        query = "判断当前激光雷达故障"
        check = response_builder.validate_query(query)
        
        assert check.refusal_message is not None
        assert "实时诊断" in check.refusal_message
        assert "自动驾驶知识检索系统" in check.refusal_message
        assert "知识检索和文档引用" in check.refusal_message
    
    def test_diagnostic_alternatives_provided(
        self,
        response_builder: ResponseBuilder,
    ) -> None:
        """Test that alternative suggestions are provided for diagnostic queries."""
        query = "诊断传感器故障"
        check = response_builder.validate_query(query)
        
        assert len(check.suggested_alternatives) > 0
        # Should suggest querying troubleshooting procedures
        alternatives_text = " ".join(check.suggested_alternatives)
        assert any(keyword in alternatives_text for keyword in ["故障排查", "流程", "方法"])


# =============================================================================
# Low Relevance Detection Tests
# =============================================================================

class TestLowRelevanceDetection:
    """Tests for low relevance detection and acknowledgment."""
    
    def test_detect_low_relevance_below_threshold(
        self,
        response_builder: ResponseBuilder,
        low_relevance_results: List[RetrievalResult],
    ) -> None:
        """Test that results below threshold trigger low relevance check."""
        check = response_builder.validate_response(
            "test query",
            low_relevance_results,
        )
        
        assert check.is_valid is False
        assert check.boundary_type == "low_relevance"
        assert check.detected_pattern is not None
        assert "low_score" in check.detected_pattern
    
    def test_detect_empty_results(
        self,
        response_builder: ResponseBuilder,
    ) -> None:
        """Test that empty results trigger low relevance check."""
        check = response_builder.validate_response("test query", [])
        
        assert check.is_valid is False
        assert check.boundary_type == "low_relevance"
        assert check.detected_pattern == "no_results"
    
    def test_low_relevance_message_generation(
        self,
        response_builder: ResponseBuilder,
        low_relevance_results: List[RetrievalResult],
    ) -> None:
        """Test low relevance message generation."""
        check = response_builder.validate_response(
            "test query",
            low_relevance_results,
        )
        
        assert check.refusal_message is not None
        assert "相关度较低" in check.refusal_message
        assert "15%" in check.refusal_message or "0.15" in check.refusal_message
    
    def test_low_relevance_alternatives_provided(
        self,
        response_builder: ResponseBuilder,
        low_relevance_results: List[RetrievalResult],
    ) -> None:
        """Test that alternative suggestions are provided for low relevance."""
        check = response_builder.validate_response(
            "test query",
            low_relevance_results,
        )
        
        assert len(check.suggested_alternatives) > 0
        alternatives_text = " ".join(check.suggested_alternatives)
        assert any(keyword in alternatives_text for keyword in ["关键词", "术语", "拆分"])
    
    def test_custom_relevance_threshold(
        self,
        response_builder: ResponseBuilder,
    ) -> None:
        """Test custom relevance threshold."""
        results = [
            RetrievalResult(
                chunk_id="test_001",
                score=0.4,
                text="Content",
                metadata={"source_path": "test.pdf"},
            )
        ]
        
        # Should pass with default threshold (0.3)
        check1 = response_builder.validate_response("test", results)
        assert check1.is_valid is True
        
        # Should fail with higher threshold (0.5)
        check2 = response_builder.validate_response(
            "test",
            results,
            relevance_threshold=0.5,
        )
        assert check2.is_valid is False
        assert check2.boundary_type == "low_relevance"


# =============================================================================
# Normal Query Tests
# =============================================================================

class TestNormalQueryValidation:
    """Tests that normal queries pass validation."""
    
    def test_sensor_query_passes_validation(
        self,
        response_builder: ResponseBuilder,
    ) -> None:
        """Test that normal sensor queries pass validation."""
        normal_queries = [
            "激光雷达的探测距离是多少",
            "摄像头的分辨率规格",
            "毫米波雷达的工作原理",
            "传感器标定流程",
        ]
        
        for query in normal_queries:
            check = response_builder.validate_query(query)
            assert check.is_valid is True, f"Query should be valid: {query}"
            assert check.boundary_type is None
    
    def test_algorithm_query_passes_validation(
        self,
        response_builder: ResponseBuilder,
    ) -> None:
        """Test that normal algorithm queries pass validation."""
        normal_queries = [
            "目标检测算法的原理",
            "路径规划算法流程",
            "PID控制参数调优",
            "SLAM算法实现方法",
        ]
        
        for query in normal_queries:
            check = response_builder.validate_query(query)
            assert check.is_valid is True
            assert check.boundary_type is None
    
    def test_regulation_query_passes_validation(
        self,
        response_builder: ResponseBuilder,
    ) -> None:
        """Test that normal regulation queries pass validation."""
        normal_queries = [
            "GB/T自动驾驶分级标准",
            "ISO 26262功能安全要求",
            "测试规范有哪些",
        ]
        
        for query in normal_queries:
            check = response_builder.validate_query(query)
            assert check.is_valid is True
            assert check.boundary_type is None
    
    def test_high_relevance_passes_validation(
        self,
        response_builder: ResponseBuilder,
        sample_ad_results: List[RetrievalResult],
    ) -> None:
        """Test that high-relevance results pass validation."""
        check = response_builder.validate_response(
            "激光雷达规格",
            sample_ad_results,
        )
        
        assert check.is_valid is True
        assert check.boundary_type is None


# =============================================================================
# Boundary Refusal Logging Tests
# =============================================================================

class TestBoundaryRefusalLogging:
    """Tests for boundary refusal logging functionality."""
    
    def test_log_predictive_refusal(
        self,
        response_builder: ResponseBuilder,
        sample_ad_results: List[RetrievalResult],
        caplog,
    ) -> None:
        """Test that predictive refusals are logged."""
        import logging
        caplog.set_level(logging.INFO)
        
        response = response_builder.build(
            results=sample_ad_results,
            query="预测下一代激光雷达性能",
            collection="ad_knowledge_v01",
        )
        
        assert response.metadata["boundary_refusal"] is True
        assert response.metadata["boundary_type"] == "predictive"
        
        # Check that refusal was logged
        assert any("boundary_refusal" in record.message.lower() for record in caplog.records)
    
    def test_log_diagnostic_refusal(
        self,
        response_builder: ResponseBuilder,
        sample_ad_results: List[RetrievalResult],
        caplog,
    ) -> None:
        """Test that diagnostic refusals are logged."""
        import logging
        caplog.set_level(logging.INFO)
        
        response = response_builder.build(
            results=sample_ad_results,
            query="判断当前传感器故障",
            collection="ad_knowledge_v01",
        )
        
        assert response.metadata["boundary_refusal"] is True
        assert response.metadata["boundary_type"] == "diagnostic"
        
        # Check that refusal was logged
        assert any("boundary_refusal" in record.message.lower() for record in caplog.records)
    
    def test_log_low_relevance_refusal(
        self,
        response_builder: ResponseBuilder,
        low_relevance_results: List[RetrievalResult],
        caplog,
    ) -> None:
        """Test that low relevance refusals are logged."""
        import logging
        caplog.set_level(logging.INFO)
        
        response = response_builder.build(
            results=low_relevance_results,
            query="test query",
            collection="ad_knowledge_v01",
        )
        
        assert response.metadata["boundary_refusal"] is True
        assert response.metadata["boundary_type"] == "low_relevance"
        
        # Check that refusal was logged
        assert any("boundary_refusal" in record.message.lower() for record in caplog.records)
    
    def test_refusal_metadata_completeness(
        self,
        response_builder: ResponseBuilder,
        sample_ad_results: List[RetrievalResult],
    ) -> None:
        """Test that refusal metadata is complete."""
        response = response_builder.build(
            results=sample_ad_results,
            query="预测传感器趋势",
            collection="ad_knowledge_v01",
        )
        
        # Check metadata completeness
        assert "boundary_refusal" in response.metadata
        assert "boundary_type" in response.metadata
        assert "detected_pattern" in response.metadata
        assert "confidence" in response.metadata
        
        assert response.metadata["boundary_refusal"] is True
        assert response.metadata["boundary_type"] == "predictive"
        assert response.metadata["detected_pattern"] is not None
        assert 0 <= response.metadata["confidence"] <= 1


# =============================================================================
# Integration Tests
# =============================================================================

class TestBoundaryValidatorIntegration:
    """Integration tests for boundary validator with full response building."""
    
    def test_predictive_query_full_response(
        self,
        response_builder: ResponseBuilder,
        sample_ad_results: List[RetrievalResult],
    ) -> None:
        """Test full response generation for predictive query."""
        response = response_builder.build(
            results=sample_ad_results,
            query="预测下一代激光雷达的性能提升",
            collection="ad_knowledge_v01",
        )
        
        # Should return refusal response
        assert response.metadata["boundary_refusal"] is True
        assert response.metadata["boundary_type"] == "predictive"
        
        # Content should contain refusal message
        assert "边界说明" in response.content
        assert "预测性分析" in response.content
        
        # Should include alternative suggestions
        assert "当前技术" in response.content or "已有" in response.content
        
        # Should include limited citations
        assert len(response.citations) <= 3
    
    def test_diagnostic_query_full_response(
        self,
        response_builder: ResponseBuilder,
        sample_ad_results: List[RetrievalResult],
    ) -> None:
        """Test full response generation for diagnostic query."""
        response = response_builder.build(
            results=sample_ad_results,
            query="判断当前激光雷达是否故障",
            collection="ad_knowledge_v01",
        )
        
        # Should return refusal response
        assert response.metadata["boundary_refusal"] is True
        assert response.metadata["boundary_type"] == "diagnostic"
        
        # Content should contain refusal message
        assert "边界说明" in response.content
        assert "实时诊断" in response.content
        
        # Should include alternative suggestions
        assert "故障排查" in response.content or "流程" in response.content
    
    def test_low_relevance_full_response(
        self,
        response_builder: ResponseBuilder,
        low_relevance_results: List[RetrievalResult],
    ) -> None:
        """Test full response generation for low relevance."""
        response = response_builder.build(
            results=low_relevance_results,
            query="不相关的查询",
            collection="ad_knowledge_v01",
        )
        
        # Should return refusal response
        assert response.metadata["boundary_refusal"] is True
        assert response.metadata["boundary_type"] == "low_relevance"
        
        # Content should contain acknowledgment
        assert "边界说明" in response.content
        assert "相关度较低" in response.content or "未找到" in response.content
        
        # Should include alternative suggestions
        assert "关键词" in response.content or "术语" in response.content
    
    def test_normal_query_full_response(
        self,
        response_builder: ResponseBuilder,
        sample_ad_results: List[RetrievalResult],
    ) -> None:
        """Test full response generation for normal query."""
        response = response_builder.build(
            results=sample_ad_results,
            query="激光雷达的探测距离和分辨率",
            collection="ad_knowledge_v01",
        )
        
        # Should return normal response
        assert response.metadata.get("boundary_refusal") is None
        
        # Content should contain search results
        assert "检索结果" in response.content
        assert "激光雷达" in response.content or "LiDAR" in response.content
        
        # Should include all citations
        assert len(response.citations) == 2


# =============================================================================
# BoundaryCheck Dataclass Tests
# =============================================================================

class TestBoundaryCheckDataclass:
    """Tests for BoundaryCheck dataclass."""
    
    def test_boundary_check_creation(self) -> None:
        """Test BoundaryCheck object creation."""
        check = BoundaryCheck(
            is_valid=False,
            boundary_type="predictive",
            refusal_message="Test message",
            suggested_alternatives=["Alt 1", "Alt 2"],
            confidence=0.85,
            detected_pattern="预测",
        )
        
        assert check.is_valid is False
        assert check.boundary_type == "predictive"
        assert check.refusal_message == "Test message"
        assert len(check.suggested_alternatives) == 2
        assert check.confidence == 0.85
        assert check.detected_pattern == "预测"
    
    def test_boundary_check_to_dict(self) -> None:
        """Test BoundaryCheck serialization."""
        check = BoundaryCheck(
            is_valid=False,
            boundary_type="diagnostic",
            refusal_message="Diagnostic refusal",
            suggested_alternatives=["Alt 1"],
            confidence=0.9,
            detected_pattern="判断当前故障",
        )
        
        check_dict = check.to_dict()
        
        assert check_dict["is_valid"] is False
        assert check_dict["boundary_type"] == "diagnostic"
        assert check_dict["refusal_message"] == "Diagnostic refusal"
        assert len(check_dict["suggested_alternatives"]) == 1
        assert check_dict["confidence"] == 0.9
        assert check_dict["detected_pattern"] == "判断当前故障"
    
    def test_boundary_check_default_values(self) -> None:
        """Test BoundaryCheck default values."""
        check = BoundaryCheck(is_valid=True)
        
        assert check.is_valid is True
        assert check.boundary_type is None
        assert check.refusal_message is None
        assert check.suggested_alternatives == []
        assert check.confidence == 1.0
        assert check.detected_pattern is None
