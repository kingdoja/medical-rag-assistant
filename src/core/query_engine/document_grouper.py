"""Document Grouper for organizing retrieval results by source document.

This module provides functionality to group retrieved chunks by their source
document and ensure document diversity for multi-document reasoning queries.

Design Principles:
- Document-aware retrieval: Group chunks by source for better context
- Diversity enforcement: Ensure multiple documents are represented
- Top-k per document: Prevent single document from dominating results
- Metadata-driven: Use chunk metadata for document identification
"""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from src.core.types import RetrievalResult

logger = logging.getLogger(__name__)


@dataclass
class DocumentGroup:
    """Represents a group of chunks from the same source document.
    
    Attributes:
        document_name: Name of the source document
        document_type: Type of document (guideline, sop, manual, training)
        chunks: List of RetrievalResult objects from this document
        total_relevance: Sum of relevance scores for all chunks
        chunk_count: Number of chunks in this group
    """
    
    document_name: str
    document_type: str
    chunks: List[RetrievalResult] = field(default_factory=list)
    total_relevance: float = 0.0
    chunk_count: int = 0
    
    def __post_init__(self):
        """Calculate derived fields after initialization."""
        if self.chunks:
            self.chunk_count = len(self.chunks)
            self.total_relevance = sum(chunk.score for chunk in self.chunks)


class DocumentGrouper:
    """Groups retrieved chunks by source document for multi-document reasoning.
    
    This component organizes retrieval results by their source document to enable
    multi-document synthesis and ensure document diversity in responses.
    
    Example:
        >>> grouper = DocumentGrouper()
        >>> grouped = grouper.group_by_document(chunks, top_k_per_doc=3)
        >>> diverse = grouper.ensure_diversity(grouped, min_docs=2)
    """
    
    def __init__(self):
        """Initialize DocumentGrouper."""
        pass
    
    def group_by_document(
        self,
        chunks: List[RetrievalResult],
        top_k_per_doc: int = 3
    ) -> Dict[str, List[RetrievalResult]]:
        """Group chunks by source document and select top-k per document.
        
        This method organizes retrieved chunks by their source document,
        ensuring that no single document dominates the results. For each
        document, only the top-k most relevant chunks are retained.
        
        Args:
            chunks: Retrieved and reranked chunks (sorted by relevance)
            top_k_per_doc: Maximum chunks to keep per document (default: 3)
            
        Returns:
            Dictionary mapping document name to list of chunks.
            Each document has at most top_k_per_doc chunks, sorted by score.
            
        Raises:
            ValueError: If top_k_per_doc is not positive
            
        Example:
            >>> chunks = [
            ...     RetrievalResult(chunk_id="doc1_c1", score=0.9, text="...", 
            ...                     metadata={"source_path": "doc1.pdf"}),
            ...     RetrievalResult(chunk_id="doc1_c2", score=0.8, text="...", 
            ...                     metadata={"source_path": "doc1.pdf"}),
            ...     RetrievalResult(chunk_id="doc2_c1", score=0.85, text="...", 
            ...                     metadata={"source_path": "doc2.pdf"}),
            ... ]
            >>> grouped = grouper.group_by_document(chunks, top_k_per_doc=2)
            >>> len(grouped["doc1.pdf"])  # 2 chunks from doc1
            2
            >>> len(grouped["doc2.pdf"])  # 1 chunk from doc2
            1
        """
        if top_k_per_doc <= 0:
            raise ValueError(f"top_k_per_doc must be positive, got {top_k_per_doc}")
        
        if not chunks:
            logger.debug("No chunks to group, returning empty dict")
            return {}
        
        # Group chunks by document name
        doc_groups: Dict[str, List[RetrievalResult]] = defaultdict(list)
        
        for chunk in chunks:
            # Extract document name from source_path metadata
            source_path = chunk.metadata.get("source_path", "unknown")
            
            # Extract just the filename from the path
            # Handle both forward and backward slashes
            doc_name = source_path.replace("\\", "/").split("/")[-1]
            
            doc_groups[doc_name].append(chunk)
        
        logger.debug(
            f"Grouped {len(chunks)} chunks into {len(doc_groups)} documents"
        )
        
        # Apply top-k selection per document
        result: Dict[str, List[RetrievalResult]] = {}
        for doc_name, doc_chunks in doc_groups.items():
            # Sort by score (descending) to ensure we keep the best chunks
            sorted_chunks = sorted(doc_chunks, key=lambda c: c.score, reverse=True)
            
            # Keep only top-k chunks
            result[doc_name] = sorted_chunks[:top_k_per_doc]
            
            logger.debug(
                f"Document '{doc_name}': kept {len(result[doc_name])} of "
                f"{len(doc_chunks)} chunks (top_k={top_k_per_doc})"
            )
        
        return result
    
    def ensure_diversity(
        self,
        grouped: Dict[str, List[RetrievalResult]],
        min_docs: int = 2
    ) -> Dict[str, List[RetrievalResult]]:
        """Ensure minimum number of source documents are represented.
        
        This method filters grouped chunks to guarantee that at least min_docs
        different source documents are included in the results. If fewer than
        min_docs documents are present, all documents are retained.
        
        Documents are prioritized by their total relevance score (sum of chunk
        scores) to ensure the most relevant documents are included.
        
        Args:
            grouped: Grouped chunks by document (from group_by_document)
            min_docs: Minimum number of documents to include (default: 2)
            
        Returns:
            Filtered grouped chunks ensuring document diversity.
            If fewer than min_docs documents exist, returns all documents.
            
        Raises:
            ValueError: If min_docs is not positive
            
        Example:
            >>> grouped = {
            ...     "doc1.pdf": [chunk1, chunk2],
            ...     "doc2.pdf": [chunk3],
            ...     "doc3.pdf": [chunk4],
            ... }
            >>> diverse = grouper.ensure_diversity(grouped, min_docs=2)
            >>> len(diverse)  # At least 2 documents
            >= 2
        """
        if min_docs <= 0:
            raise ValueError(f"min_docs must be positive, got {min_docs}")
        
        if not grouped:
            logger.debug("No grouped chunks, returning empty dict")
            return {}
        
        # If we already have enough documents, return as-is
        if len(grouped) <= min_docs:
            logger.debug(
                f"Already have {len(grouped)} documents (min_docs={min_docs}), "
                "no filtering needed"
            )
            return grouped
        
        # Calculate total relevance for each document
        doc_relevance: List[Tuple[str, float]] = []
        for doc_name, chunks in grouped.items():
            total_score = sum(chunk.score for chunk in chunks)
            doc_relevance.append((doc_name, total_score))
        
        # Sort by total relevance (descending)
        doc_relevance.sort(key=lambda x: x[1], reverse=True)
        
        # Keep top min_docs documents
        selected_docs = {doc_name for doc_name, _ in doc_relevance[:min_docs]}
        
        result = {
            doc_name: chunks
            for doc_name, chunks in grouped.items()
            if doc_name in selected_docs
        }
        
        logger.debug(
            f"Ensured diversity: kept {len(result)} of {len(grouped)} documents "
            f"(min_docs={min_docs})"
        )
        
        return result
    
    def get_document_groups(
        self,
        chunks: List[RetrievalResult],
        top_k_per_doc: int = 3
    ) -> List[DocumentGroup]:
        """Group chunks and return structured DocumentGroup objects.
        
        This is a convenience method that combines grouping with metadata
        extraction to produce DocumentGroup objects with document type
        and relevance information.
        
        Args:
            chunks: Retrieved and reranked chunks
            top_k_per_doc: Maximum chunks to keep per document
            
        Returns:
            List of DocumentGroup objects, sorted by total_relevance (descending)
            
        Example:
            >>> groups = grouper.get_document_groups(chunks, top_k_per_doc=3)
            >>> for group in groups:
            ...     print(f"{group.document_name}: {group.chunk_count} chunks, "
            ...           f"relevance={group.total_relevance:.2f}")
        """
        grouped = self.group_by_document(chunks, top_k_per_doc)
        
        document_groups: List[DocumentGroup] = []
        for doc_name, doc_chunks in grouped.items():
            # Extract document type from metadata (if available)
            doc_type = "unknown"
            if doc_chunks:
                doc_type = doc_chunks[0].metadata.get("doc_type", "unknown")
            
            group = DocumentGroup(
                document_name=doc_name,
                document_type=doc_type,
                chunks=doc_chunks
            )
            document_groups.append(group)
        
        # Sort by total relevance (descending)
        document_groups.sort(key=lambda g: g.total_relevance, reverse=True)
        
        return document_groups


def create_document_grouper() -> DocumentGrouper:
    """Factory function to create DocumentGrouper.
    
    Returns:
        Configured DocumentGrouper instance
    """
    return DocumentGrouper()
