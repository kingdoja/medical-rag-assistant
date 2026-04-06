"""Unit tests for ResponseBuilder scope integration."""

import pytest
from unittest.mock import Mock

from src.core.response.response_builder import ResponseBuilder
from src.core.query_engine.scope_provider import ScopeProvider, ScopeInfo


class TestResponseBuilderScope:
    """Test suite for ResponseBuilder scope integration."""
    
    def test_build_scope_response_with_provider(self):
        """Test building scope response with configured provider."""
        # Setup mock scope provider
        mock_provider = Mock(spec=ScopeProvider)
        
        # Mock scope info
        mock_scope = ScopeInfo(
            collection="medical_demo_v01",
            document_types={"guideline", "sop", "manual"},
            document_count=5,
            chunk_count=200,
            last_updated="2024-01-15T10:30:00",
            coverage_areas=["样本运输", "质量管理"],
        )
        mock_provider.get_collection_scope.return_value = mock_scope
        
        # Mock formatted response
        mock_response = "## 知识库范围说明\n\n当前知识库包含5个文档..."
        mock_provider.format_scope_response.return_value = mock_response
        
        # Create response builder with scope provider
        builder = ResponseBuilder(scope_provider=mock_provider)
        
        # Build scope response
        response = builder.build_scope_response(
            query="知识库里有哪些资料？",
            collection="medical_demo_v01"
        )
        
        # Verify provider was called
        mock_provider.get_collection_scope.assert_called_once_with("medical_demo_v01")
        mock_provider.format_scope_response.assert_called_once()
        
        # Verify response structure
        assert response.content == mock_response
        assert response.metadata["scope_query"] is True
        assert response.metadata["collection"] == "medical_demo_v01"
        assert response.metadata["document_count"] == 5
        assert "guideline" in response.metadata["document_types"]
        assert "sop" in response.metadata["document_types"]
        assert "manual" in response.metadata["document_types"]
        assert response.is_empty is False
        assert len(response.citations) == 0
    
    def test_build_scope_response_without_provider(self):
        """Test building scope response without configured provider (fallback)."""
        # Create response builder without scope provider
        builder = ResponseBuilder()
        
        # Build scope response (should use fallback)
        response = builder.build_scope_response(
            query="知识库里有哪些资料？",
            collection="medical_demo_v01"
        )
        
        # Verify fallback response
        assert "知识库范围说明" in response.content
        assert "知识库里有哪些资料？" in response.content
        assert "指南文档" in response.content
        assert "标准操作程序" in response.content
        assert "设备说明书" in response.content
        assert "培训材料" in response.content
        assert "medical_demo_v01" in response.content
        
        # Verify metadata
        assert response.metadata["scope_query"] is True
        assert response.metadata["fallback"] is True
        assert response.metadata["collection"] == "medical_demo_v01"
        assert response.is_empty is False
    
    def test_build_scope_response_provider_error(self):
        """Test building scope response when provider raises error."""
        # Setup mock scope provider that raises error
        mock_provider = Mock(spec=ScopeProvider)
        mock_provider.get_collection_scope.side_effect = Exception("Database error")
        
        # Create response builder with failing provider
        builder = ResponseBuilder(scope_provider=mock_provider)
        
        # Build scope response (should fall back)
        response = builder.build_scope_response(
            query="知识库里有哪些资料？",
            collection="test_collection"
        )
        
        # Verify fallback was used
        assert "知识库范围说明" in response.content
        assert response.metadata["scope_query"] is True
        assert response.metadata["fallback"] is True
    
    def test_set_scope_provider(self):
        """Test setting scope provider after initialization."""
        # Create response builder without provider
        builder = ResponseBuilder()
        assert builder.scope_provider is None
        
        # Create and set provider
        mock_provider = Mock(spec=ScopeProvider)
        builder.set_scope_provider(mock_provider)
        
        # Verify provider is set
        assert builder.scope_provider is mock_provider
    
    def test_build_scope_response_no_collection(self):
        """Test building scope response without collection name."""
        # Setup mock scope provider
        mock_provider = Mock(spec=ScopeProvider)
        
        # Mock scope info without collection
        mock_scope = ScopeInfo(
            collection="default",
            document_types={"guideline"},
            document_count=2,
            chunk_count=50,
            last_updated="2024-01-15T10:30:00",
        )
        mock_provider.get_collection_scope.return_value = mock_scope
        mock_provider.format_scope_response.return_value = "## 知识库范围说明\n\n..."
        
        # Create response builder
        builder = ResponseBuilder(scope_provider=mock_provider)
        
        # Build scope response without collection
        response = builder.build_scope_response(query="知识库范围是什么？")
        
        # Verify provider was called with None
        mock_provider.get_collection_scope.assert_called_once_with(None)
        
        # Verify response
        assert response.metadata["scope_query"] is True
        assert response.metadata["collection"] == "default"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
