"""Unit tests for ScopeProvider."""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock
from dataclasses import dataclass

from src.core.query_engine.scope_provider import ScopeProvider, ScopeInfo


@dataclass
class MockDocumentInfo:
    """Mock DocumentInfo for testing."""
    source_path: str
    source_hash: str
    collection: str = "test_collection"
    chunk_count: int = 10
    image_count: int = 2
    processed_at: str = "2024-01-15T10:30:00"


@dataclass
class MockCollectionStats:
    """Mock CollectionStats for testing."""
    collection: str = "test_collection"
    document_count: int = 3
    chunk_count: int = 30
    image_count: int = 6


class TestScopeProvider:
    """Test suite for ScopeProvider."""
    
    def test_get_collection_scope_basic(self):
        """Test basic scope information retrieval."""
        # Setup mock document manager
        mock_doc_mgr = Mock()
        
        # Mock collection stats
        mock_stats = MockCollectionStats(
            collection="medical_demo_v01",
            document_count=3,
            chunk_count=150,
            image_count=10,
        )
        mock_doc_mgr.get_collection_stats.return_value = mock_stats
        
        # Mock document list
        mock_docs = [
            MockDocumentInfo(
                source_path="demo-data/guidelines/guideline_lab_quality.pdf",
                source_hash="hash1",
                processed_at="2024-01-15T10:30:00",
            ),
            MockDocumentInfo(
                source_path="demo-data/sops/sop_sample_management.pdf",
                source_hash="hash2",
                processed_at="2024-01-16T11:00:00",
            ),
            MockDocumentInfo(
                source_path="demo-data/manuals/manual_histocore_user.pdf",
                source_hash="hash3",
                processed_at="2024-01-17T09:15:00",
            ),
        ]
        mock_doc_mgr.list_documents.return_value = mock_docs
        
        # Create provider
        provider = ScopeProvider(document_manager=mock_doc_mgr)
        
        # Get scope
        scope = provider.get_collection_scope("medical_demo_v01")
        
        # Verify basic fields
        assert scope.collection == "medical_demo_v01"
        assert scope.document_count == 3
        assert scope.chunk_count == 150
        
        # Verify document types detected
        assert "guideline" in scope.document_types
        assert "sop" in scope.document_types
        assert "manual" in scope.document_types
        
        # Verify document list
        assert len(scope.document_list) == 3
        
        # Verify last updated (should be most recent)
        assert scope.last_updated == "2024-01-17T09:15:00"
    
    def test_get_collection_scope_empty(self):
        """Test scope retrieval for empty collection."""
        # Setup mock document manager
        mock_doc_mgr = Mock()
        
        # Mock empty collection
        mock_stats = MockCollectionStats(
            collection="empty_collection",
            document_count=0,
            chunk_count=0,
            image_count=0,
        )
        mock_doc_mgr.get_collection_stats.return_value = mock_stats
        mock_doc_mgr.list_documents.return_value = []
        
        # Create provider
        provider = ScopeProvider(document_manager=mock_doc_mgr)
        
        # Get scope
        scope = provider.get_collection_scope("empty_collection")
        
        # Verify empty collection
        assert scope.collection == "empty_collection"
        assert scope.document_count == 0
        assert scope.chunk_count == 0
        assert len(scope.document_types) == 0
        assert len(scope.document_list) == 0
        assert scope.last_updated is not None  # Should have current timestamp
    
    def test_detect_document_type_guideline(self):
        """Test document type detection for guidelines."""
        mock_doc_mgr = Mock()
        provider = ScopeProvider(document_manager=mock_doc_mgr)
        
        # Test various guideline patterns
        assert provider._detect_document_type("guideline_lab_quality.pdf") == "guideline"
        assert provider._detect_document_type("WHO_指南_transport.pdf") == "guideline"
        assert provider._detect_document_type("quality_guide.pdf") == "guideline"
    
    def test_detect_document_type_sop(self):
        """Test document type detection for SOPs."""
        mock_doc_mgr = Mock()
        provider = ScopeProvider(document_manager=mock_doc_mgr)
        
        # Test various SOP patterns
        assert provider._detect_document_type("sop_sample_management.pdf") == "sop"
        assert provider._detect_document_type("标准操作程序_quality.pdf") == "sop"
        assert provider._detect_document_type("procedure_document.pdf") == "sop"
    
    def test_detect_document_type_manual(self):
        """Test document type detection for manuals."""
        mock_doc_mgr = Mock()
        provider = ScopeProvider(document_manager=mock_doc_mgr)
        
        # Test various manual patterns
        assert provider._detect_document_type("manual_histocore_user.pdf") == "manual"
        assert provider._detect_document_type("设备说明书_microscope.pdf") == "manual"
        assert provider._detect_document_type("user_manual_device.pdf") == "manual"
    
    def test_detect_document_type_training(self):
        """Test document type detection for training materials."""
        mock_doc_mgr = Mock()
        provider = ScopeProvider(document_manager=mock_doc_mgr)
        
        # Test various training patterns
        assert provider._detect_document_type("training_quality_control.pdf") == "training"
        assert provider._detect_document_type("培训材料_safety.pdf") == "training"
        assert provider._detect_document_type("tutorial_basics.pdf") == "training"
    
    def test_detect_document_type_unknown(self):
        """Test document type detection for unknown types."""
        mock_doc_mgr = Mock()
        provider = ScopeProvider(document_manager=mock_doc_mgr)
        
        # Test unknown document
        assert provider._detect_document_type("random_document.pdf") is None
        assert provider._detect_document_type("report_2024.pdf") is None
    
    def test_extract_coverage_areas(self):
        """Test coverage area extraction from document names."""
        mock_doc_mgr = Mock()
        provider = ScopeProvider(document_manager=mock_doc_mgr)
        
        # Test document list
        doc_list = [
            "guideline_transport_infectious_substances.pdf",
            "sop_sample_management_procedures.pdf",
            "manual_equipment_maintenance.pdf",
            "training_quality_control_basics.pdf",
        ]
        
        coverage = provider._extract_coverage_areas(doc_list)
        
        # Verify coverage areas extracted
        assert "样本运输" in coverage  # transport
        assert "样本管理" in coverage  # sample
        assert "设备管理" in coverage  # equipment
        assert "质量管理" in coverage  # quality
        assert "培训" in coverage  # training
    
    def test_format_scope_response_with_query(self):
        """Test scope response formatting with query context."""
        # Setup mock document manager
        mock_doc_mgr = Mock()
        provider = ScopeProvider(document_manager=mock_doc_mgr)
        
        # Create scope info
        scope = ScopeInfo(
            collection="medical_demo_v01",
            document_types={"guideline", "sop", "manual"},
            document_count=5,
            chunk_count=200,
            last_updated="2024-01-15T10:30:00",
            coverage_areas=["样本运输", "质量管理", "设备管理"],
        )
        
        # Format response
        response = provider.format_scope_response(scope, query="知识库里有哪些资料？")
        
        # Verify response structure
        assert "知识库范围说明" in response
        assert "知识库里有哪些资料？" in response
        assert "文档类型" in response
        assert "指南文档" in response
        assert "标准操作程序" in response
        assert "设备说明书" in response
        assert "覆盖领域" in response
        assert "样本运输" in response
        assert "质量管理" in response
        assert "统计信息" in response
        assert "**文档总数:** 5" in response
        assert "**知识片段数:** 200" in response
        assert "使用建议" in response
        assert "medical_demo_v01" in response
    
    def test_format_scope_response_without_query(self):
        """Test scope response formatting without query context."""
        # Setup mock document manager
        mock_doc_mgr = Mock()
        provider = ScopeProvider(document_manager=mock_doc_mgr)
        
        # Create scope info
        scope = ScopeInfo(
            collection="test_collection",
            document_types={"guideline"},
            document_count=2,
            chunk_count=50,
            last_updated="2024-01-15T10:30:00",
        )
        
        # Format response without query
        response = provider.format_scope_response(scope)
        
        # Verify response structure
        assert "知识库范围说明" in response
        assert "当前知识库的覆盖范围如下" in response
        assert "文档类型" in response
        assert "统计信息" in response
    
    def test_format_timestamp(self):
        """Test timestamp formatting."""
        mock_doc_mgr = Mock()
        provider = ScopeProvider(document_manager=mock_doc_mgr)
        
        # Test valid ISO timestamp
        formatted = provider._format_timestamp("2024-01-15T10:30:00")
        assert "2024" in formatted
        assert "01" in formatted
        assert "15" in formatted
        
        # Test None timestamp
        assert provider._format_timestamp(None) == "未知"
        
        # Test invalid timestamp
        invalid = provider._format_timestamp("invalid")
        assert invalid == "invalid"
    
    def test_scope_info_to_dict(self):
        """Test ScopeInfo serialization to dict."""
        scope = ScopeInfo(
            collection="test_collection",
            document_types={"guideline", "sop"},
            document_count=3,
            chunk_count=100,
            last_updated="2024-01-15T10:30:00",
            document_list=["doc1.pdf", "doc2.pdf"],
            coverage_areas=["area1", "area2"],
        )
        
        scope_dict = scope.to_dict()
        
        # Verify dict structure
        assert scope_dict["collection"] == "test_collection"
        assert set(scope_dict["document_types"]) == {"guideline", "sop"}
        assert scope_dict["document_count"] == 3
        assert scope_dict["chunk_count"] == 100
        assert scope_dict["last_updated"] == "2024-01-15T10:30:00"
        assert scope_dict["document_list"] == ["doc1.pdf", "doc2.pdf"]
        assert scope_dict["coverage_areas"] == ["area1", "area2"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestScopeProviderAD:
    """Test suite for ScopeProvider autonomous driving domain support."""

    def _make_provider(self, docs=None, doc_count=0, chunk_count=0):
        """Helper to create a ScopeProvider with mocked document manager."""
        from unittest.mock import Mock
        mock_doc_mgr = Mock()
        mock_doc_mgr.get_collection_stats.return_value = MockCollectionStats(
            collection="ad_knowledge_v01",
            document_count=doc_count,
            chunk_count=chunk_count,
        )
        mock_doc_mgr.list_documents.return_value = docs or []
        return ScopeProvider(document_manager=mock_doc_mgr)

    def test_detect_ad_sensor_doc(self):
        """Test detection of AD sensor document types."""
        provider = self._make_provider()
        assert provider._detect_document_type("lidar_spec_vls128.pdf") == "sensor_doc"
        assert provider._detect_document_type("camera_spec_ov2311.pdf") == "sensor_doc"
        assert provider._detect_document_type("radar_spec_ars408.pdf") == "sensor_doc"
        assert provider._detect_document_type("calibration_doc_lidar.pdf") == "sensor_doc"

    def test_detect_ad_algorithm_doc(self):
        """Test detection of AD algorithm document types."""
        provider = self._make_provider()
        assert provider._detect_document_type("perception_design_yolo.pdf") == "algorithm_doc"
        assert provider._detect_document_type("planning_design_rrt.pdf") == "algorithm_doc"
        assert provider._detect_document_type("control_design_pid.pdf") == "algorithm_doc"

    def test_detect_ad_regulation_doc(self):
        """Test detection of AD regulation document types."""
        provider = self._make_provider()
        assert provider._detect_document_type("gb_t_40429_2021.pdf") == "regulation_doc"
        assert provider._detect_document_type("iso_26262_part3.pdf") == "regulation_doc"
        assert provider._detect_document_type("test_specification_acc.pdf") == "regulation_doc"

    def test_detect_ad_test_doc(self):
        """Test detection of AD test document types."""
        provider = self._make_provider()
        assert provider._detect_document_type("test_scenario_following.pdf") == "test_doc"
        assert provider._detect_document_type("functional_test_acc.pdf") == "test_doc"
        assert provider._detect_document_type("safety_test_braking.pdf") == "test_doc"
        assert provider._detect_document_type("test_case_lane_change.pdf") == "test_doc"

    def test_get_document_statistics(self):
        """Test get_document_statistics returns per-type counts."""
        docs = [
            MockDocumentInfo(source_path="sensor_spec/lidar_spec_vls128.pdf", source_hash="h1"),
            MockDocumentInfo(source_path="sensor_spec/camera_spec_ov2311.pdf", source_hash="h2"),
            MockDocumentInfo(source_path="algorithms/perception_design_yolo.pdf", source_hash="h3"),
            MockDocumentInfo(source_path="regulations/gb_t_40429_2021.pdf", source_hash="h4"),
            MockDocumentInfo(source_path="tests/test_scenario_following.pdf", source_hash="h5"),
            MockDocumentInfo(source_path="tests/functional_test_acc.pdf", source_hash="h6"),
        ]
        provider = self._make_provider(docs=docs, doc_count=6)
        stats = provider.get_document_statistics("ad_knowledge_v01")

        assert stats.get("sensor_doc", 0) == 2
        assert stats.get("algorithm_doc", 0) == 1
        assert stats.get("regulation_doc", 0) == 1
        assert stats.get("test_doc", 0) == 2

    def test_get_document_statistics_empty(self):
        """Test get_document_statistics with empty collection."""
        provider = self._make_provider()
        stats = provider.get_document_statistics("ad_knowledge_v01")
        assert stats == {}

    def test_format_ad_scope_response_basic(self):
        """Test AD scope response formatting."""
        provider = self._make_provider()
        scope = ScopeInfo(
            collection="ad_knowledge_v01",
            document_types={"sensor_doc", "algorithm_doc", "regulation_doc", "test_doc"},
            document_count=260,
            chunk_count=1200,
            last_updated="2024-01-15T10:30:00",
            coverage_areas=["传感器技术", "感知算法", "法规标准", "测试场景"],
        )
        stats = {"sensor_doc": 50, "algorithm_doc": 80, "regulation_doc": 30, "test_doc": 100}

        response = provider.format_ad_scope_response(scope, statistics=stats)

        assert "ad_knowledge_v01" in response
        assert "传感器文档" in response
        assert "算法文档" in response
        assert "法规文档" in response
        assert "测试文档" in response
        assert "260" in response
        assert "1200" in response

    def test_format_ad_scope_response_with_query(self):
        """Test AD scope response includes query context."""
        provider = self._make_provider()
        scope = ScopeInfo(
            collection="ad_knowledge_v01",
            document_types={"sensor_doc"},
            document_count=50,
            chunk_count=500,
            last_updated="2024-01-15T10:30:00",
        )

        response = provider.format_ad_scope_response(scope, query="系统包含哪些文档？")
        assert "系统包含哪些文档？" in response

    def test_format_ad_scope_response_with_counts(self):
        """Test AD scope response shows per-type document counts."""
        provider = self._make_provider()
        scope = ScopeInfo(
            collection="ad_knowledge_v01",
            document_types={"sensor_doc", "algorithm_doc"},
            document_count=130,
            chunk_count=800,
            last_updated="2024-01-15T10:30:00",
        )
        stats = {"sensor_doc": 50, "algorithm_doc": 80}

        response = provider.format_ad_scope_response(scope, statistics=stats)
        assert "50 份" in response
        assert "80 份" in response

    def test_medical_types_still_detected(self):
        """Test that medical domain types are still detected (backward compat)."""
        provider = self._make_provider()
        assert provider._detect_document_type("guideline_lab_quality.pdf") == "guideline"
        assert provider._detect_document_type("sop_sample_management.pdf") == "sop"
        assert provider._detect_document_type("manual_histocore_user.pdf") == "manual"
