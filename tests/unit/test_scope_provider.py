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
