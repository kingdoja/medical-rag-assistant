"""Citation Enhancer for enriching citations with detailed metadata.

This module enhances basic citations with additional metadata extraction,
authority scoring, and ranking to support P1 multi-document reasoning scenarios.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional

from src.core.types import RetrievalResult


@dataclass
class EnhancedCitation:
    """Enhanced citation with detailed metadata for better traceability.
    
    Attributes:
        document_name: Name of the source document
        document_type: Type classification (guideline, sop, manual, training)
        section: Section or chapter name (if extractable)
        page: Page number in source document (if available)
        relevance_score: Retrieval relevance score (0-1)
        authority_score: Document authority score based on type (0-1)
        excerpt: Key sentence or phrase from the chunk
        chunk_id: Unique identifier for the source chunk
        metadata: Additional metadata from the chunk
    """
    
    document_name: str
    document_type: Literal["guideline", "sop", "manual", "training", "unknown"]
    relevance_score: float
    authority_score: float
    excerpt: str
    chunk_id: str
    section: Optional[str] = None
    page: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            "document_name": self.document_name,
            "document_type": self.document_type,
            "relevance_score": round(self.relevance_score, 4),
            "authority_score": round(self.authority_score, 4),
            "excerpt": self.excerpt,
            "chunk_id": self.chunk_id,
        }
        if self.section is not None:
            result["section"] = self.section
        if self.page is not None:
            result["page"] = self.page
        if self.metadata:
            result["metadata"] = self.metadata
        return result


class CitationEnhancer:
    """Enhances citations with detailed metadata and authority scoring.
    
    This class extracts document metadata, calculates authority scores,
    and ranks citations for multi-document reasoning scenarios.
    
    Example:
        >>> enhancer = CitationEnhancer()
        >>> result = RetrievalResult(chunk_id="doc1_001", score=0.95, ...)
        >>> citation = enhancer.enhance_citation(result)
        >>> print(citation.document_type)  # "guideline"
        >>> print(citation.authority_score)  # 1.0
    """
    
    # Document type patterns for classification
    # Order matters: more specific patterns should come first
    _DOC_TYPE_PATTERNS = {
        "sop": [
            r"sop",
            r"标准操作程序",
            r"操作规程",
            r"作业指导",
            r"程序文件",
        ],
        "guideline": [
            r"guideline",
            r"指南",
            r"规范",
            r"标准",
            r"准则",
            r"who.*guideline",
            r"质量管理",
        ],
        "manual": [
            r"manual",
            r"说明书",
            r"用户手册",
            r"操作手册",
            r"使用手册",
            r"user.*manual",
        ],
        "training": [
            r"training",
            r"培训",
            r"教程",
            r"课程",
            r"学习",
        ],
    }
    
    # Authority scores by document type (higher = more authoritative)
    _AUTHORITY_SCORES = {
        "guideline": 1.0,
        "sop": 0.8,
        "manual": 0.6,
        "training": 0.4,
        "unknown": 0.3,
    }
    
    # Section header patterns (Markdown and common formats)
    _SECTION_PATTERNS = [
        r"^#{1,6}\s+(.+)$",  # Markdown headers
        r"^第[一二三四五六七八九十\d]+[章节部分]\s+(.+)$",  # Chinese chapter/section
        r"^[一二三四五六七八九十\d]+[、\.]\s+(.+)$",  # Numbered sections
        r"^\d+\.\d+\s+(.+)$",  # Decimal numbering (1.1, 2.3, etc.)
    ]
    
    def __init__(
        self,
        excerpt_max_length: int = 150,
        include_metadata_fields: Optional[List[str]] = None,
    ) -> None:
        """Initialize CitationEnhancer.
        
        Args:
            excerpt_max_length: Maximum characters for excerpt (default: 150)
            include_metadata_fields: Optional list of metadata fields to preserve.
                If None, includes 'title', 'chunk_index', 'source_path'.
        """
        self.excerpt_max_length = excerpt_max_length
        self.include_metadata_fields = include_metadata_fields or [
            "title",
            "chunk_index",
            "source_path",
        ]
    
    def enhance_citation(self, result: RetrievalResult) -> EnhancedCitation:
        """Enhance a retrieval result with detailed citation metadata.
        
        Args:
            result: RetrievalResult from search/retrieval.
            
        Returns:
            EnhancedCitation with extracted metadata and scores.
        """
        metadata = result.metadata or {}
        
        # Extract document name from source_path
        document_name = self._extract_document_name(metadata)
        
        # Classify document type
        document_type = self._classify_document_type(document_name, metadata)
        
        # Calculate authority score
        authority_score = self._AUTHORITY_SCORES[document_type]
        
        # Extract section from text
        section = self._extract_section(result.text)
        
        # Extract page number
        page = self._extract_page(metadata)
        
        # Generate excerpt
        excerpt = self._generate_excerpt(result.text)
        
        # Preserve selected metadata fields
        extra_metadata = {}
        for field_name in self.include_metadata_fields:
            if field_name in metadata:
                extra_metadata[field_name] = metadata[field_name]
        
        return EnhancedCitation(
            document_name=document_name,
            document_type=document_type,
            section=section,
            page=page,
            relevance_score=result.score,
            authority_score=authority_score,
            excerpt=excerpt,
            chunk_id=result.chunk_id,
            metadata=extra_metadata,
        )
    
    def rank_citations(
        self,
        citations: List[EnhancedCitation],
    ) -> List[EnhancedCitation]:
        """Rank citations by relevance and authority.
        
        Priority order:
        1. Relevance score (primary)
        2. Authority score (tie-breaker)
        3. Document name (alphabetical, for stability)
        
        Args:
            citations: List of EnhancedCitation objects.
            
        Returns:
            Sorted list of citations (highest priority first).
        """
        return sorted(
            citations,
            key=lambda c: (
                -c.relevance_score,  # Higher relevance first
                -c.authority_score,  # Higher authority first
                c.document_name,  # Alphabetical for stability
            ),
        )
    
    def format_citation(
        self,
        citation: EnhancedCitation,
        index: int,
        style: Literal["inline", "reference", "detailed"] = "reference",
    ) -> str:
        """Format an enhanced citation for display.
        
        Args:
            citation: EnhancedCitation to format.
            index: 1-based citation index.
            style: Formatting style:
                - "inline": Brief inline marker like "[1]"
                - "reference": Reference list format like "[1] document.pdf (p.5)"
                - "detailed": Full details including section and excerpt
                
        Returns:
            Formatted citation string.
        """
        if style == "inline":
            return f"[{index}]"
        
        elif style == "reference":
            parts = [f"[{index}]", f"`{citation.document_name}`"]
            if citation.page is not None:
                parts.append(f"(p.{citation.page})")
            return " ".join(parts)
        
        elif style == "detailed":
            lines = [
                f"[{index}] **{citation.document_name}**",
                f"  - 类型: {citation.document_type}",
                f"  - 相关度: {citation.relevance_score:.2%}",
            ]
            if citation.section:
                lines.append(f"  - 章节: {citation.section}")
            if citation.page is not None:
                lines.append(f"  - 页码: {citation.page}")
            lines.append(f"  - 摘录: {citation.excerpt}")
            return "\n".join(lines)
        
        else:
            raise ValueError(f"Unknown citation style: {style}")
    
    def _extract_document_name(self, metadata: Dict[str, Any]) -> str:
        """Extract document name from metadata.
        
        Args:
            metadata: Chunk metadata.
            
        Returns:
            Document name (filename without path).
        """
        source_path = metadata.get("source_path", "unknown")
        
        # Extract filename from path
        if "/" in source_path:
            return source_path.split("/")[-1]
        elif "\\" in source_path:
            return source_path.split("\\")[-1]
        else:
            return source_path
    
    def _classify_document_type(
        self,
        document_name: str,
        metadata: Dict[str, Any],
    ) -> Literal["guideline", "sop", "manual", "training", "unknown"]:
        """Classify document type based on name and metadata.
        
        Args:
            document_name: Name of the document.
            metadata: Chunk metadata (may contain 'doc_type' field).
            
        Returns:
            Document type classification.
        """
        # Check if doc_type is explicitly set in metadata
        if "doc_type" in metadata:
            doc_type = metadata["doc_type"].lower()
            if doc_type in self._AUTHORITY_SCORES:
                return doc_type  # type: ignore
        
        # Pattern matching on document name
        name_lower = document_name.lower()
        
        for doc_type, patterns in self._DOC_TYPE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, name_lower, re.IGNORECASE):
                    return doc_type  # type: ignore
        
        return "unknown"
    
    def _extract_section(self, text: str) -> Optional[str]:
        """Extract section header from chunk text.
        
        Args:
            text: Chunk text content.
            
        Returns:
            Section name if found, None otherwise.
        """
        if not text:
            return None
        
        # Check first few lines for section headers
        lines = text.split("\n")[:5]  # Check first 5 lines
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            for pattern in self._SECTION_PATTERNS:
                match = re.match(pattern, line)
                if match:
                    section_name = match.group(1).strip()
                    # Remove trailing punctuation
                    section_name = section_name.rstrip("：:。.")
                    return section_name
        
        return None
    
    def _extract_page(self, metadata: Dict[str, Any]) -> Optional[int]:
        """Extract page number from metadata.
        
        Args:
            metadata: Chunk metadata.
            
        Returns:
            Page number if available, None otherwise.
        """
        page = metadata.get("page") or metadata.get("page_num")
        if page is not None:
            try:
                return int(page)
            except (ValueError, TypeError):
                return None
        return None
    
    def _generate_excerpt(self, text: str) -> str:
        """Generate a concise excerpt from chunk text.
        
        Args:
            text: Full chunk text.
            
        Returns:
            Truncated excerpt with ellipsis if needed.
        """
        if not text:
            return ""
        
        # Clean up whitespace
        cleaned = " ".join(text.split())
        
        if len(cleaned) <= self.excerpt_max_length:
            return cleaned
        
        # Truncate at word boundary
        truncated = cleaned[:self.excerpt_max_length].rsplit(" ", 1)[0]
        return truncated + "..."
