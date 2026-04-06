"""Unit tests for DocumentGrouper.

Tests document grouping, diversity enforcement, and top-k selection.
"""

import pytest
from src.core.query_engine.document_grouper import (
    DocumentGrouper,
    DocumentGroup,
    create_document_grouper,
)
from src.core.types import RetrievalResult


class TestDocumentGrouper:
    """Test suite for DocumentGrouper."""
    
    def test_group_by_document_basic(self):
        """Test basic document grouping functionality."""
        grouper = DocumentGrouper()
        
        chunks = [
            RetrievalResult(
                chunk_id="doc1_c1",
                score=0.9,
                text="Content from doc1",
                metadata={"source_path": "data/documents/doc1.pdf"}
            ),
            RetrievalResult(
                chunk_id="doc1_c2",
                score=0.8,
                text="More content from doc1",
                metadata={"source_path": "data/documents/doc1.pdf"}
            ),
            RetrievalResult(
                chunk_id="doc2_c1",
                score=0.85,
                text="Content from doc2",
                metadata={"source_path": "data/documents/doc2.pdf"}
            ),
        ]
        
        grouped = grouper.group_by_document(chunks, top_k_per_doc=3)
        
        assert len(grouped) == 2
        assert "doc1.pdf" in grouped
        assert "doc2.pdf" in grouped
        assert len(grouped["doc1.pdf"]) == 2
        assert len(grouped["doc2.pdf"]) == 1
    
    def test_group_by_document_top_k_limit(self):
        """Test top-k selection per document."""
        grouper = DocumentGrouper()
        
        chunks = [
            RetrievalResult(
                chunk_id="doc1_c1",
                score=0.9,
                text="Content 1",
                metadata={"source_path": "doc1.pdf"}
            ),
            RetrievalResult(
                chunk_id="doc1_c2",
                score=0.8,
                text="Content 2",
                metadata={"source_path": "doc1.pdf"}
            ),
            RetrievalResult(
                chunk_id="doc1_c3",
                score=0.7,
                text="Content 3",
                metadata={"source_path": "doc1.pdf"}
            ),
            RetrievalResult(
                chunk_id="doc1_c4",
                score=0.6,
                text="Content 4",
                metadata={"source_path": "doc1.pdf"}
            ),
        ]
        
        grouped = grouper.group_by_document(chunks, top_k_per_doc=2)
        
        assert len(grouped["doc1.pdf"]) == 2
        # Should keep the top 2 by score
        assert grouped["doc1.pdf"][0].chunk_id == "doc1_c1"
        assert grouped["doc1.pdf"][1].chunk_id == "doc1_c2"
    
    def test_group_by_document_empty_chunks(self):
        """Test handling of empty chunk list."""
        grouper = DocumentGrouper()
        
        grouped = grouper.group_by_document([], top_k_per_doc=3)
        
        assert len(grouped) == 0
    
    def test_group_by_document_invalid_top_k(self):
        """Test error handling for invalid top_k_per_doc."""
        grouper = DocumentGrouper()
        
        chunks = [
            RetrievalResult(
                chunk_id="c1",
                score=0.9,
                text="Content",
                metadata={"source_path": "doc1.pdf"}
            ),
        ]
        
        with pytest.raises(ValueError, match="top_k_per_doc must be positive"):
            grouper.group_by_document(chunks, top_k_per_doc=0)
        
        with pytest.raises(ValueError, match="top_k_per_doc must be positive"):
            grouper.group_by_document(chunks, top_k_per_doc=-1)
    
    def test_ensure_diversity_basic(self):
        """Test basic diversity enforcement."""
        grouper = DocumentGrouper()
        
        grouped = {
            "doc1.pdf": [
                RetrievalResult(
                    chunk_id="doc1_c1",
                    score=0.9,
                    text="Content",
                    metadata={"source_path": "doc1.pdf"}
                ),
            ],
            "doc2.pdf": [
                RetrievalResult(
                    chunk_id="doc2_c1",
                    score=0.8,
                    text="Content",
                    metadata={"source_path": "doc2.pdf"}
                ),
            ],
            "doc3.pdf": [
                RetrievalResult(
                    chunk_id="doc3_c1",
                    score=0.7,
                    text="Content",
                    metadata={"source_path": "doc3.pdf"}
                ),
            ],
        }
        
        diverse = grouper.ensure_diversity(grouped, min_docs=2)
        
        assert len(diverse) == 2
        # Should keep the top 2 by total relevance
        assert "doc1.pdf" in diverse
        assert "doc2.pdf" in diverse
    
    def test_ensure_diversity_already_diverse(self):
        """Test diversity enforcement when already diverse enough."""
        grouper = DocumentGrouper()
        
        grouped = {
            "doc1.pdf": [
                RetrievalResult(
                    chunk_id="doc1_c1",
                    score=0.9,
                    text="Content",
                    metadata={"source_path": "doc1.pdf"}
                ),
            ],
            "doc2.pdf": [
                RetrievalResult(
                    chunk_id="doc2_c1",
                    score=0.8,
                    text="Content",
                    metadata={"source_path": "doc2.pdf"}
                ),
            ],
        }
        
        diverse = grouper.ensure_diversity(grouped, min_docs=3)
        
        # Should return all documents since we have fewer than min_docs
        assert len(diverse) == 2
        assert "doc1.pdf" in diverse
        assert "doc2.pdf" in diverse
    
    def test_ensure_diversity_empty_grouped(self):
        """Test handling of empty grouped dict."""
        grouper = DocumentGrouper()
        
        diverse = grouper.ensure_diversity({}, min_docs=2)
        
        assert len(diverse) == 0
    
    def test_ensure_diversity_invalid_min_docs(self):
        """Test error handling for invalid min_docs."""
        grouper = DocumentGrouper()
        
        grouped = {
            "doc1.pdf": [
                RetrievalResult(
                    chunk_id="c1",
                    score=0.9,
                    text="Content",
                    metadata={"source_path": "doc1.pdf"}
                ),
            ],
        }
        
        with pytest.raises(ValueError, match="min_docs must be positive"):
            grouper.ensure_diversity(grouped, min_docs=0)
        
        with pytest.raises(ValueError, match="min_docs must be positive"):
            grouper.ensure_diversity(grouped, min_docs=-1)
    
    def test_ensure_diversity_prioritizes_by_total_relevance(self):
        """Test that diversity enforcement prioritizes by total relevance."""
        grouper = DocumentGrouper()
        
        grouped = {
            "doc1.pdf": [
                RetrievalResult(chunk_id="doc1_c1", score=0.5, text="", metadata={"source_path": "doc1.pdf"}),
                RetrievalResult(chunk_id="doc1_c2", score=0.5, text="", metadata={"source_path": "doc1.pdf"}),
            ],  # Total: 1.0
            "doc2.pdf": [
                RetrievalResult(chunk_id="doc2_c1", score=0.9, text="", metadata={"source_path": "doc2.pdf"}),
            ],  # Total: 0.9
            "doc3.pdf": [
                RetrievalResult(chunk_id="doc3_c1", score=0.3, text="", metadata={"source_path": "doc3.pdf"}),
            ],  # Total: 0.3
        }
        
        diverse = grouper.ensure_diversity(grouped, min_docs=2)
        
        assert len(diverse) == 2
        assert "doc1.pdf" in diverse  # Highest total relevance
        assert "doc2.pdf" in diverse  # Second highest
        assert "doc3.pdf" not in diverse  # Lowest
    
    def test_get_document_groups(self):
        """Test getting structured DocumentGroup objects."""
        grouper = DocumentGrouper()
        
        chunks = [
            RetrievalResult(
                chunk_id="doc1_c1",
                score=0.9,
                text="Content",
                metadata={"source_path": "doc1.pdf", "doc_type": "guideline"}
            ),
            RetrievalResult(
                chunk_id="doc1_c2",
                score=0.8,
                text="Content",
                metadata={"source_path": "doc1.pdf", "doc_type": "guideline"}
            ),
            RetrievalResult(
                chunk_id="doc2_c1",
                score=0.85,
                text="Content",
                metadata={"source_path": "doc2.pdf", "doc_type": "sop"}
            ),
        ]
        
        groups = grouper.get_document_groups(chunks, top_k_per_doc=3)
        
        assert len(groups) == 2
        assert isinstance(groups[0], DocumentGroup)
        
        # Should be sorted by total relevance (descending)
        assert groups[0].total_relevance >= groups[1].total_relevance
        
        # Check metadata
        for group in groups:
            assert group.document_name in ["doc1.pdf", "doc2.pdf"]
            assert group.chunk_count > 0
            assert group.total_relevance > 0
    
    def test_get_document_groups_extracts_doc_type(self):
        """Test that get_document_groups extracts document type from metadata."""
        grouper = DocumentGrouper()
        
        chunks = [
            RetrievalResult(
                chunk_id="doc1_c1",
                score=0.9,
                text="Content",
                metadata={"source_path": "doc1.pdf", "doc_type": "manual"}
            ),
        ]
        
        groups = grouper.get_document_groups(chunks, top_k_per_doc=3)
        
        assert len(groups) == 1
        assert groups[0].document_type == "manual"
    
    def test_get_document_groups_handles_missing_doc_type(self):
        """Test that get_document_groups handles missing doc_type gracefully."""
        grouper = DocumentGrouper()
        
        chunks = [
            RetrievalResult(
                chunk_id="doc1_c1",
                score=0.9,
                text="Content",
                metadata={"source_path": "doc1.pdf"}
            ),
        ]
        
        groups = grouper.get_document_groups(chunks, top_k_per_doc=3)
        
        assert len(groups) == 1
        assert groups[0].document_type == "unknown"
    
    def test_factory_function(self):
        """Test factory function creates valid grouper."""
        grouper = create_document_grouper()
        
        assert isinstance(grouper, DocumentGrouper)
        
        # Verify it works
        chunks = [
            RetrievalResult(
                chunk_id="c1",
                score=0.9,
                text="Content",
                metadata={"source_path": "doc1.pdf"}
            ),
        ]
        grouped = grouper.group_by_document(chunks, top_k_per_doc=3)
        assert len(grouped) == 1
    
    def test_document_group_post_init(self):
        """Test DocumentGroup post_init calculates derived fields."""
        chunks = [
            RetrievalResult(
                chunk_id="c1",
                score=0.9,
                text="Content",
                metadata={"source_path": "doc1.pdf"}
            ),
            RetrievalResult(
                chunk_id="c2",
                score=0.8,
                text="Content",
                metadata={"source_path": "doc1.pdf"}
            ),
        ]
        
        group = DocumentGroup(
            document_name="doc1.pdf",
            document_type="guideline",
            chunks=chunks
        )
        
        assert group.chunk_count == 2
        assert abs(group.total_relevance - 1.7) < 0.001  # 0.9 + 0.8 (with floating point tolerance)
    
    def test_group_by_document_handles_path_separators(self):
        """Test that document grouping handles different path separators."""
        grouper = DocumentGrouper()
        
        chunks = [
            RetrievalResult(
                chunk_id="c1",
                score=0.9,
                text="Content",
                metadata={"source_path": "data/documents/doc1.pdf"}
            ),
            RetrievalResult(
                chunk_id="c2",
                score=0.8,
                text="Content",
                metadata={"source_path": "data\\documents\\doc1.pdf"}  # Windows path
            ),
        ]
        
        grouped = grouper.group_by_document(chunks, top_k_per_doc=3)
        
        # Both should be grouped under the same document name
        assert len(grouped) == 1
        assert "doc1.pdf" in grouped
        assert len(grouped["doc1.pdf"]) == 2
