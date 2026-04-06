"""Response builder for MCP tool output."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Union, Tuple

try:
    from mcp import types
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    # Create placeholder types for when mcp is not available
    class types:
        class TextContent:
            def __init__(self, type: str, text: str):
                self.type = type
                self.text = text
        
        class ImageContent:
            def __init__(self, type: str, data: str, mimeType: str):
                self.type = type
                self.data = data
                self.mimeType = mimeType

from src.core.response.citation_generator import Citation, CitationGenerator
from src.core.response.citation_enhancer import CitationEnhancer, EnhancedCitation
from src.core.types import RetrievalResult

logger = logging.getLogger(__name__)


@dataclass
class BoundaryCheck:
    """Result of boundary validation for a query.
    
    Attributes:
        is_valid: Whether the query is within system boundaries
        boundary_type: Type of boundary violation if invalid
        refusal_message: Human-readable refusal message
        suggested_alternatives: List of alternative query suggestions
        confidence: Confidence score for the boundary detection (0-1)
        detected_pattern: The specific pattern that triggered the boundary check
    """
    
    is_valid: bool
    boundary_type: Optional[Literal["diagnostic", "predictive", "low_relevance"]] = None
    refusal_message: Optional[str] = None
    suggested_alternatives: List[str] = field(default_factory=list)
    confidence: float = 1.0
    detected_pattern: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "is_valid": self.is_valid,
            "boundary_type": self.boundary_type,
            "refusal_message": self.refusal_message,
            "suggested_alternatives": self.suggested_alternatives,
            "confidence": self.confidence,
            "detected_pattern": self.detected_pattern,
        }


@dataclass
class MCPToolResponse:
    """Structured response for MCP tools."""

    content: str
    citations: List[Citation] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_empty: bool = False
    image_contents: List[types.ImageContent] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to a dict-like MCP payload."""
        return {
            "content": self.content,
            "structuredContent": {
                "citations": [citation.to_dict() for citation in self.citations],
                "metadata": self.metadata,
                "isEmpty": self.is_empty,
            },
        }

    def to_mcp_content(self) -> List[Union[types.TextContent, types.ImageContent]]:
        """Convert response to MCP content blocks."""
        blocks: List[Union[types.TextContent, types.ImageContent]] = [
            types.TextContent(type="text", text=self.content)
        ]

        if self.image_contents:
            blocks.extend(self.image_contents)

        if self.citations or self.metadata:
            import json

            structured = {
                "citations": [citation.to_dict() for citation in self.citations],
                "metadata": self.metadata,
                "has_images": len(self.image_contents) > 0,
                "image_count": len(self.image_contents),
            }
            blocks.append(
                types.TextContent(
                    type="text",
                    text=(
                        "\n---\n**References (JSON):**\n```json\n"
                        f"{json.dumps(structured, ensure_ascii=False, indent=2)}\n```"
                    ),
                )
            )

        return blocks

    @property
    def has_images(self) -> bool:
        """Whether the response includes image blocks."""
        return len(self.image_contents) > 0


class ResponseBuilder:
    """Build MCP-formatted responses from retrieval results."""

    _DIAGNOSTIC_PATTERNS: Tuple[str, ...] = (
        "是不是某种疾病",
        "是不是疾病",
        "是不是癌",
        "是不是肿瘤",
        "给我诊断",
        "直接告诉我结果",
        "帮我诊断",
        "是否为某种疾病",
        "是什么病",
        "病理诊断",
        "临床诊断",
        "diagnose",
        "diagnosis",
        "what disease",
        "is this cancer",
        "does this mean i have",
    )
    
    _PREDICTIVE_PATTERNS: Tuple[str, ...] = (
        "预测",
        "下个月",
        "最常见",
        "会发生",
        "将会",
        "未来",
        "可能发生",
        "预计",
        "预期",
        "趋势",
        "predict",
        "forecast",
        "will happen",
        "most likely",
        "in the future",
    )
    
    # Low relevance threshold for boundary checking
    _LOW_RELEVANCE_THRESHOLD: float = 0.3

    def __init__(
        self,
        citation_generator: Optional[CitationGenerator] = None,
        citation_enhancer: Optional[CitationEnhancer] = None,
        multimodal_assembler: Optional["MultimodalAssembler"] = None,
        scope_provider: Optional["ScopeProvider"] = None,
        max_results_in_content: int = 5,
        snippet_max_length: int = 300,
        enable_multimodal: bool = True,
    ) -> None:
        self.citation_generator = citation_generator or CitationGenerator()
        self.citation_enhancer = citation_enhancer or CitationEnhancer()
        self.max_results_in_content = max_results_in_content
        self.snippet_max_length = snippet_max_length
        self.enable_multimodal = enable_multimodal
        self._multimodal_assembler = multimodal_assembler
        self._scope_provider = scope_provider

    @property
    def multimodal_assembler(self) -> "MultimodalAssembler":
        """Get or create the multimodal assembler lazily."""
        if self._multimodal_assembler is None:
            from src.core.response.multimodal_assembler import MultimodalAssembler

            self._multimodal_assembler = MultimodalAssembler()
        return self._multimodal_assembler
    
    @property
    def scope_provider(self) -> Optional["ScopeProvider"]:
        """Get the scope provider if available."""
        return self._scope_provider
    
    def set_scope_provider(self, scope_provider: "ScopeProvider") -> None:
        """Set the scope provider for knowledge base scope queries.
        
        Args:
            scope_provider: ScopeProvider instance
        """
        self._scope_provider = scope_provider

    def build(
        self,
        results: List[RetrievalResult],
        query: str,
        collection: Optional[str] = None,
        include_images: bool = True,
    ) -> MCPToolResponse:
        """Build an MCP response from retrieval results."""
        # Validate query boundaries
        query_check = self.validate_query(query)
        if not query_check.is_valid:
            self._log_boundary_refusal(query, query_check)
            return self._build_enhanced_boundary_response(
                results=results,
                query=query,
                collection=collection,
                boundary_check=query_check,
            )
        
        # Validate response relevance
        response_check = self.validate_response(query, results)
        if not response_check.is_valid:
            self._log_boundary_refusal(query, response_check)
            return self._build_enhanced_boundary_response(
                results=results,
                query=query,
                collection=collection,
                boundary_check=response_check,
            )

        if not results:
            return self._build_empty_response(query, collection)

        citations = self.citation_generator.generate(results)
        content = self._build_markdown_content(results, citations, query)
        metadata = self._build_metadata(query, collection, len(results))

        image_contents: List[types.ImageContent] = []
        if self.enable_multimodal and include_images:
            image_blocks = self.multimodal_assembler.assemble(results, collection)
            image_contents = [
                block for block in image_blocks if isinstance(block, types.ImageContent)
            ]
            if image_contents:
                metadata["has_images"] = True
                metadata["image_count"] = len(image_contents)

        return MCPToolResponse(
            content=content,
            citations=citations,
            metadata=metadata,
            is_empty=False,
            image_contents=image_contents,
        )

    def _is_diagnostic_boundary_query(self, query: str) -> bool:
        """Return True when the query asks for diagnosis-like conclusions."""
        normalized = " ".join((query or "").strip().lower().split())
        if not normalized:
            return False
        return any(pattern in normalized for pattern in self._DIAGNOSTIC_PATTERNS)
    
    def validate_query(self, query: str) -> BoundaryCheck:
        """Validate if query is within system boundaries.
        
        Checks for:
        1. Diagnostic queries (existing)
        2. Predictive queries (new)
        
        Args:
            query: User query string
            
        Returns:
            BoundaryCheck with validation result
        """
        normalized = " ".join((query or "").strip().lower().split())
        if not normalized:
            return BoundaryCheck(is_valid=True)
        
        # Check for diagnostic patterns
        for pattern in self._DIAGNOSTIC_PATTERNS:
            if pattern in normalized:
                return BoundaryCheck(
                    is_valid=False,
                    boundary_type="diagnostic",
                    refusal_message=self._generate_diagnostic_refusal_message(query),
                    suggested_alternatives=self._get_diagnostic_alternatives(),
                    confidence=0.9,
                    detected_pattern=pattern,
                )
        
        # Check for predictive patterns
        for pattern in self._PREDICTIVE_PATTERNS:
            if pattern in normalized:
                return BoundaryCheck(
                    is_valid=False,
                    boundary_type="predictive",
                    refusal_message=self._generate_predictive_refusal_message(query),
                    suggested_alternatives=self._get_predictive_alternatives(),
                    confidence=0.85,
                    detected_pattern=pattern,
                )
        
        return BoundaryCheck(is_valid=True)
    
    def validate_response(
        self,
        query: str,
        results: List[RetrievalResult],
        relevance_threshold: Optional[float] = None,
    ) -> BoundaryCheck:
        """Validate if retrieved results are relevant enough to answer.
        
        Args:
            query: User query string
            results: Retrieved results with relevance scores
            relevance_threshold: Minimum score for top result (default: 0.3)
            
        Returns:
            BoundaryCheck indicating if response should be generated
        """
        threshold = relevance_threshold or self._LOW_RELEVANCE_THRESHOLD
        
        if not results:
            return BoundaryCheck(
                is_valid=False,
                boundary_type="low_relevance",
                refusal_message=self._generate_low_relevance_message(query),
                suggested_alternatives=self._get_low_relevance_alternatives(),
                confidence=1.0,
                detected_pattern="no_results",
            )
        
        # Check top result relevance
        top_score = results[0].score
        if top_score < threshold:
            return BoundaryCheck(
                is_valid=False,
                boundary_type="low_relevance",
                refusal_message=self._generate_low_relevance_message(query, top_score),
                suggested_alternatives=self._get_low_relevance_alternatives(),
                confidence=0.8,
                detected_pattern=f"low_score_{top_score:.2f}",
            )
        
        return BoundaryCheck(is_valid=True)
    
    def _generate_diagnostic_refusal_message(self, query: str) -> str:
        """Generate refusal message for diagnostic queries."""
        return (
            f"查询 **\"{query}\"** 涉及诊断性或高风险医疗判断请求。\n"
            "PathoMind 当前只提供知识检索、规范引用、培训和流程辅助，"
            "不提供疾病诊断、病理结论或临床决策建议。"
        )
    
    def _generate_predictive_refusal_message(self, query: str) -> str:
        """Generate refusal message for predictive queries."""
        return (
            f"查询 **\"{query}\"** 涉及预测性分析请求。\n"
            "PathoMind 当前只提供基于现有文档的事实性信息检索，"
            "不提供预测、趋势分析或未来事件判断。\n\n"
            "**建议改为查询：**\n"
            "- 历史数据和已记录的案例\n"
            "- 相关的指南、SOP 或培训材料\n"
            "- 设备操作规范和质量控制流程"
        )
    
    def _generate_low_relevance_message(
        self, 
        query: str, 
        top_score: Optional[float] = None
    ) -> str:
        """Generate message for low-relevance scenarios."""
        if top_score is not None:
            return (
                f"查询 **\"{query}\"** 的检索结果相关度较低（最高相关度: {top_score:.2%}）。\n"
                "当前知识库中可能没有直接相关的资料。"
            )
        return f"查询 **\"{query}\"** 未找到相关结果。\n当前知识库中可能没有相关的资料。"
    
    def _get_diagnostic_alternatives(self) -> List[str]:
        """Get alternative suggestions for diagnostic queries."""
        return [
            "这个结果相关的 SOP、指南或说明书依据是什么？",
            "遇到类似情况时，实验室内部要求的复核或上报流程是什么？",
            "当前知识库里有哪些资料可以帮助人工复核？",
        ]
    
    def _get_predictive_alternatives(self) -> List[str]:
        """Get alternative suggestions for predictive queries."""
        return [
            "查询相关的历史数据和已记录案例",
            "查找相关的指南、SOP 或培训材料",
            "了解设备操作规范和质量控制流程",
            "查询相关的统计数据和研究报告",
        ]
    
    def _get_low_relevance_alternatives(self) -> List[str]:
        """Get alternative suggestions for low-relevance queries."""
        return [
            "尝试使用更具体的关键词或术语",
            "确认相关资料是否已经完成导入（ingest）",
            "如果问题涉及设备或流程，请包含设备名称或流程名称",
            "尝试将复杂问题拆分为多个简单问题",
        ]
    
    def _log_boundary_refusal(
        self,
        query: str,
        boundary_check: BoundaryCheck,
    ) -> None:
        """Log boundary refusal events for analysis.
        
        Args:
            query: The user query that was refused
            boundary_check: The boundary check result
        """
        log_entry = {
            "event": "boundary_refusal",
            "query": query,
            "boundary_type": boundary_check.boundary_type,
            "detected_pattern": boundary_check.detected_pattern,
            "confidence": boundary_check.confidence,
        }
        logger.info("Boundary refusal: %s", log_entry)

    def _build_boundary_response(
        self,
        results: List[RetrievalResult],
        query: str,
        collection: Optional[str],
    ) -> MCPToolResponse:
        """Build a refusal response for diagnostic or high-risk medical queries."""
        citations = self.citation_generator.generate(results)
        reference_citations = citations[: min(3, len(citations))]

        lines = [
            "## 边界说明",
            "",
            f"查询 **\"{query}\"** 涉及诊断性或高风险医疗判断请求。",
            "PathoMind 当前只提供知识检索、规范引用、培训和流程辅助，"
            "不提供疾病诊断、病理结论或临床决策建议。",
            "",
            "**你可以改问这些更安全的问题：**",
            "- 这个结果相关的 SOP、指南或说明书依据是什么？",
            "- 遇到类似情况时，实验室内部要求的复核或上报流程是什么？",
            "- 当前知识库里有哪些资料可以帮助人工复核？",
        ]

        if reference_citations:
            lines.extend(
                [
                    "",
                    "**可回看的资料范围：**",
                    *[
                        f"- [{citation.index}] `{citation.source}`"
                        + (f" (p.{citation.page})" if citation.page is not None else "")
                        for citation in reference_citations
                    ],
                ]
            )
        else:
            lines.extend(
                [
                    "",
                    "当前没有匹配到可直接引用的资料，请改成规范、流程或设备操作类问题后再检索。",
                ]
            )

        metadata = self._build_metadata(query, collection, len(results))
        metadata["boundary_refusal"] = True
        metadata["boundary_category"] = "diagnostic_request"

        return MCPToolResponse(
            content="\n".join(lines),
            citations=reference_citations,
            metadata=metadata,
            is_empty=False,
            image_contents=[],
        )
    
    def _build_enhanced_boundary_response(
        self,
        results: List[RetrievalResult],
        query: str,
        collection: Optional[str],
        boundary_check: BoundaryCheck,
    ) -> MCPToolResponse:
        """Build an enhanced refusal response for boundary violations.
        
        Args:
            results: Retrieved results (may be empty or low-relevance)
            query: User query
            collection: Collection name
            boundary_check: Boundary check result with refusal details
            
        Returns:
            MCPToolResponse with refusal message and guidance
        """
        citations = self.citation_generator.generate(results) if results else []
        reference_citations = citations[: min(3, len(citations))]

        lines = [
            "## 边界说明",
            "",
            boundary_check.refusal_message or "",
        ]
        
        # Add specific guidance based on boundary type
        if boundary_check.suggested_alternatives:
            lines.extend(
                [
                    "",
                    "**你可以改问这些问题：**",
                    *[f"- {alt}" for alt in boundary_check.suggested_alternatives],
                ]
            )
        
        # Add reference citations if available and relevant
        if reference_citations and boundary_check.boundary_type != "low_relevance":
            lines.extend(
                [
                    "",
                    "**可参考的资料：**",
                    *[
                        f"- [{citation.index}] `{citation.source}`"
                        + (f" (p.{citation.page})" if citation.page is not None else "")
                        for citation in reference_citations
                    ],
                ]
            )
        elif boundary_check.boundary_type == "low_relevance":
            lines.extend(
                [
                    "",
                    "当前知识库中没有找到直接相关的资料。",
                ]
            )

        metadata = self._build_metadata(query, collection, len(results))
        metadata["boundary_refusal"] = True
        metadata["boundary_type"] = boundary_check.boundary_type
        metadata["detected_pattern"] = boundary_check.detected_pattern
        metadata["confidence"] = boundary_check.confidence

        return MCPToolResponse(
            content="\n".join(lines),
            citations=reference_citations,
            metadata=metadata,
            is_empty=False,
            image_contents=[],
        )

    def _build_empty_response(
        self,
        query: str,
        collection: Optional[str] = None,
    ) -> MCPToolResponse:
        """Build a response for empty retrieval results."""
        lines = [
            "## 未找到相关结果",
            "",
            f"查询: **{query}**",
            "",
        ]

        if collection:
            lines.append(f"在集合 `{collection}` 中未找到与该问题相关的资料。")
        else:
            lines.append("未找到与该问题相关的资料。")

        lines.extend(
            [
                "",
                "**建议：**",
                "- 尝试换一组更具体的关键词",
                "- 先确认相关资料是否已经完成 ingest",
                "- 如果问题涉及设备或流程，优先带上设备名、流程名或规范主题",
            ]
        )

        return MCPToolResponse(
            content="\n".join(lines),
            citations=[],
            metadata=self._build_metadata(query, collection, 0),
            is_empty=True,
        )

    def _build_markdown_content(
        self,
        results: List[RetrievalResult],
        citations: List[Citation],
        query: str,
    ) -> str:
        """Build the standard retrieval response body."""
        lines = [
            "## 检索结果",
            "",
            f"针对查询 **\"{query}\"** 找到 {len(results)} 条相关结果。",
            "",
        ]

        display_count = min(len(results), self.max_results_in_content)

        for result, citation in zip(results[:display_count], citations[:display_count]):
            marker = self.citation_generator.format_citation_marker(citation.index)
            lines.append(f"### {marker} 结果 {citation.index}")
            lines.append(f"**相关度:** {citation.score:.2%}")
            lines.append(f"**来源:** `{citation.source}`")
            if citation.page is not None:
                lines.append(f"**页码:** {citation.page}")
            snippet = self._truncate_text(result.text, self.snippet_max_length)
            lines.append("")
            lines.append(f"> {snippet}")
            lines.append("")

        if len(results) > display_count:
            remaining = len(results) - display_count
            lines.append(f"*...还有 {remaining} 条结果未显示*")
            lines.append("")

        lines.append("---")
        lines.append("")
        lines.append("## 引用来源")
        lines.append("")

        for citation in citations:
            source_info = f"`{citation.source}`"
            if citation.page is not None:
                source_info += f" (p.{citation.page})"
            lines.append(f"- [{citation.index}] {source_info}")

        return "\n".join(lines)

    def _build_metadata(
        self,
        query: str,
        collection: Optional[str],
        result_count: int,
    ) -> Dict[str, Any]:
        """Build response metadata."""
        metadata: Dict[str, Any] = {
            "query": query,
            "result_count": result_count,
        }
        if collection:
            metadata["collection"] = collection
        return metadata
    
    def build_multi_document_response(
        self,
        query: str,
        grouped_chunks: Dict[str, List[RetrievalResult]],
        response_type: Literal["comparison", "aggregation", "standard"],
        collection: Optional[str] = None,
        include_images: bool = True,
    ) -> MCPToolResponse:
        """Build response synthesizing information from multiple documents.
        
        This method creates structured responses for multi-document queries,
        with different formatting based on the response type:
        
        - comparison: Shows similarities and differences with clear attribution
        - aggregation: Lists key points from multiple sources with citations
        - standard: Synthesizes information coherently with citations
        
        Args:
            query: User query string
            grouped_chunks: Dictionary mapping document name to list of chunks
            response_type: Type of multi-document response to build
            collection: Collection name (optional)
            include_images: Whether to include image content (default: True)
            
        Returns:
            MCPToolResponse with multi-document synthesis and enhanced citations
            
        Example:
            >>> grouped = {
            ...     "guideline1.pdf": [chunk1, chunk2],
            ...     "guideline2.pdf": [chunk3, chunk4],
            ... }
            >>> response = builder.build_multi_document_response(
            ...     query="WHO运输指南和质量管理指南有什么不同？",
            ...     grouped_chunks=grouped,
            ...     response_type="comparison"
            ... )
        """
        # Flatten chunks for citation generation
        all_chunks: List[RetrievalResult] = []
        for chunks in grouped_chunks.values():
            all_chunks.extend(chunks)
        
        if not all_chunks:
            return self._build_empty_response(query, collection)
        
        # Generate enhanced citations
        enhanced_citations = [
            self.citation_enhancer.enhance_citation(chunk)
            for chunk in all_chunks
        ]
        
        # Rank citations by relevance and authority
        ranked_citations = self.citation_enhancer.rank_citations(enhanced_citations)
        
        # Build content based on response type
        if response_type == "comparison":
            content = self._build_comparison_content(
                query, grouped_chunks, ranked_citations
            )
        elif response_type == "aggregation":
            content = self._build_aggregation_content(
                query, grouped_chunks, ranked_citations
            )
        else:  # standard
            content = self._build_standard_multi_doc_content(
                query, grouped_chunks, ranked_citations
            )
        
        # Convert enhanced citations to standard citations for compatibility
        standard_citations = self._convert_to_standard_citations(ranked_citations)
        
        # Build metadata
        metadata = self._build_metadata(query, collection, len(all_chunks))
        metadata["response_type"] = response_type
        metadata["document_count"] = len(grouped_chunks)
        metadata["multi_document"] = True
        
        # Handle images if enabled
        image_contents: List[types.ImageContent] = []
        if self.enable_multimodal and include_images:
            image_blocks = self.multimodal_assembler.assemble(all_chunks, collection)
            image_contents = [
                block for block in image_blocks if isinstance(block, types.ImageContent)
            ]
            if image_contents:
                metadata["has_images"] = True
                metadata["image_count"] = len(image_contents)
        
        return MCPToolResponse(
            content=content,
            citations=standard_citations,
            metadata=metadata,
            is_empty=False,
            image_contents=image_contents,
        )
    
    def _build_comparison_content(
        self,
        query: str,
        grouped_chunks: Dict[str, List[RetrievalResult]],
        citations: List[EnhancedCitation],
    ) -> str:
        """Build comparison response with clear attribution.
        
        Format: "根据 [Doc A]，... 而根据 [Doc B]，..."
        
        Args:
            query: User query
            grouped_chunks: Chunks grouped by document
            citations: Enhanced citations ranked by relevance
            
        Returns:
            Formatted comparison response
        """
        lines = [
            "## 对比分析",
            "",
            f"针对查询 **\"{query}\"**，以下是不同文档的对比：",
            "",
        ]
        
        # Get document names sorted by total relevance
        doc_relevance = [
            (doc_name, sum(c.score for c in chunks))
            for doc_name, chunks in grouped_chunks.items()
        ]
        doc_relevance.sort(key=lambda x: x[1], reverse=True)
        
        # Build comparison for each document
        for idx, (doc_name, _) in enumerate(doc_relevance, 1):
            chunks = grouped_chunks[doc_name]
            
            # Find citations for this document
            doc_citations = [
                c for c in citations if c.document_name == doc_name
            ]
            
            if not doc_citations:
                continue
            
            # Get citation indices
            citation_indices = [
                citations.index(c) + 1 for c in doc_citations
            ]
            citation_markers = ", ".join(f"[{i}]" for i in citation_indices)
            
            # Build document section
            lines.append(f"### {idx}. 根据 `{doc_name}` {citation_markers}")
            lines.append("")
            
            # Add top chunk excerpt
            if chunks:
                top_chunk = chunks[0]
                excerpt = self._truncate_text(top_chunk.text, 200)
                lines.append(f"> {excerpt}")
                lines.append("")
            
            # Add document type and relevance info
            if doc_citations:
                doc_type_cn = self._translate_doc_type(doc_citations[0].document_type)
                lines.append(f"**文档类型:** {doc_type_cn}")
                lines.append(f"**相关度:** {doc_citations[0].relevance_score:.2%}")
                lines.append("")
        
        # Add comparison summary
        if len(doc_relevance) >= 2:
            lines.extend([
                "---",
                "",
                "**对比要点:**",
                "",
                "以上内容来自不同文档，请根据具体需求选择参考。",
                "如需更详细的对比，建议查阅完整文档。",
                "",
            ])
        
        # Add citations section
        lines.extend(self._build_citations_section(citations))
        
        return "\n".join(lines)
    
    def _build_aggregation_content(
        self,
        query: str,
        grouped_chunks: Dict[str, List[RetrievalResult]],
        citations: List[EnhancedCitation],
    ) -> str:
        """Build aggregation response with numbered points and citations.
        
        Format: "1. [Point] (来源: [Doc A]) 2. [Point] (来源: [Doc B])"
        
        Args:
            query: User query
            grouped_chunks: Chunks grouped by document
            citations: Enhanced citations ranked by relevance
            
        Returns:
            Formatted aggregation response
        """
        lines = [
            "## 综合汇总",
            "",
            f"针对查询 **\"{query}\"**，从多个文档中汇总如下：",
            "",
        ]
        
        # Collect key points from each document
        point_num = 1
        for doc_name, chunks in grouped_chunks.items():
            if not chunks:
                continue
            
            # Find citations for this document
            doc_citations = [
                c for c in citations if c.document_name == doc_name
            ]
            
            if not doc_citations:
                continue
            
            # Get citation index
            citation_idx = citations.index(doc_citations[0]) + 1
            
            # Add point from top chunk
            top_chunk = chunks[0]
            excerpt = self._truncate_text(top_chunk.text, 150)
            
            lines.append(f"{point_num}. {excerpt}")
            lines.append(f"   - **来源:** `{doc_name}` [{citation_idx}]")
            lines.append(f"   - **相关度:** {top_chunk.score:.2%}")
            lines.append("")
            
            point_num += 1
            
            # Limit to 5 points for readability
            if point_num > 5:
                break
        
        # Add summary note
        lines.extend([
            "---",
            "",
            f"**汇总说明:** 以上内容来自 {len(grouped_chunks)} 个文档，",
            "涵盖了查询的主要相关信息。详细内容请参考引用来源。",
            "",
        ])
        
        # Add citations section
        lines.extend(self._build_citations_section(citations))
        
        return "\n".join(lines)
    
    def _build_standard_multi_doc_content(
        self,
        query: str,
        grouped_chunks: Dict[str, List[RetrievalResult]],
        citations: List[EnhancedCitation],
    ) -> str:
        """Build standard multi-document response with coherent synthesis.
        
        Args:
            query: User query
            grouped_chunks: Chunks grouped by document
            citations: Enhanced citations ranked by relevance
            
        Returns:
            Formatted standard response
        """
        lines = [
            "## 检索结果",
            "",
            f"针对查询 **\"{query}\"**，从 {len(grouped_chunks)} 个文档中找到相关信息：",
            "",
        ]
        
        # Show top results from each document
        result_num = 1
        for doc_name, chunks in grouped_chunks.items():
            if not chunks:
                continue
            
            # Find citations for this document
            doc_citations = [
                c for c in citations if c.document_name == doc_name
            ]
            
            if not doc_citations:
                continue
            
            # Get citation index
            citation_idx = citations.index(doc_citations[0]) + 1
            
            # Add result section
            top_chunk = chunks[0]
            lines.append(f"### [{citation_idx}] 结果 {result_num} - `{doc_name}`")
            lines.append(f"**相关度:** {top_chunk.score:.2%}")
            
            if doc_citations[0].section:
                lines.append(f"**章节:** {doc_citations[0].section}")
            if doc_citations[0].page is not None:
                lines.append(f"**页码:** {doc_citations[0].page}")
            
            excerpt = self._truncate_text(top_chunk.text, self.snippet_max_length)
            lines.append("")
            lines.append(f"> {excerpt}")
            lines.append("")
            
            result_num += 1
            
            # Limit display count
            if result_num > self.max_results_in_content:
                break
        
        # Add remaining documents note
        if len(grouped_chunks) > result_num - 1:
            remaining = len(grouped_chunks) - (result_num - 1)
            lines.append(f"*...还有 {remaining} 个文档的结果未显示*")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        
        # Add citations section
        lines.extend(self._build_citations_section(citations))
        
        return "\n".join(lines)
    
    def _build_citations_section(
        self,
        citations: List[EnhancedCitation],
    ) -> List[str]:
        """Build the citations reference section.
        
        Args:
            citations: Enhanced citations to format
            
        Returns:
            List of formatted citation lines
        """
        lines = [
            "## 引用来源",
            "",
        ]
        
        for idx, citation in enumerate(citations, 1):
            # Format citation with enhanced metadata
            parts = [f"[{idx}]", f"`{citation.document_name}`"]
            
            # Add document type
            doc_type_cn = self._translate_doc_type(citation.document_type)
            parts.append(f"({doc_type_cn})")
            
            # Add page if available
            if citation.page is not None:
                parts.append(f"p.{citation.page}")
            
            # Add section if available
            if citation.section:
                parts.append(f"- {citation.section}")
            
            lines.append(" ".join(parts))
        
        return lines
    
    def _convert_to_standard_citations(
        self,
        enhanced_citations: List[EnhancedCitation],
    ) -> List[Citation]:
        """Convert enhanced citations to standard citations for compatibility.
        
        Args:
            enhanced_citations: List of EnhancedCitation objects
            
        Returns:
            List of standard Citation objects
        """
        standard_citations: List[Citation] = []
        
        for idx, enhanced in enumerate(enhanced_citations, 1):
            citation = Citation(
                index=idx,
                chunk_id=enhanced.chunk_id,
                source=enhanced.document_name,
                score=enhanced.relevance_score,
                text_snippet=enhanced.excerpt,
                page=enhanced.page,
                metadata={
                    "doc_type": enhanced.document_type,
                    "section": enhanced.section,
                    "authority_score": enhanced.authority_score,
                },
            )
            standard_citations.append(citation)
        
        return standard_citations
    
    def _translate_doc_type(
        self,
        doc_type: str,
    ) -> str:
        """Translate document type to Chinese.
        
        Args:
            doc_type: Document type in English
            
        Returns:
            Chinese translation
        """
        translations = {
            "guideline": "指南",
            "sop": "SOP",
            "manual": "说明书",
            "training": "培训材料",
            "unknown": "其他",
        }
        return translations.get(doc_type, doc_type)

    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to a readable snippet length."""
        if not text:
            return ""

        cleaned = " ".join(text.split())
        if len(cleaned) <= max_length:
            return cleaned

        truncated = cleaned[:max_length].rsplit(" ", 1)[0]
        return truncated + "..."
    
    def build_scope_response(
        self,
        query: str,
        collection: Optional[str] = None,
    ) -> MCPToolResponse:
        """Build a response describing knowledge base scope.
        
        This method handles S12 scope queries by providing information
        about what the system knows, including document types, counts,
        and coverage areas.
        
        Args:
            query: User query (typically asking about scope)
            collection: Collection name (optional)
            
        Returns:
            MCPToolResponse with scope information
            
        Example:
            >>> response = builder.build_scope_response(
            ...     query="知识库里有哪些资料？",
            ...     collection="medical_demo_v01"
            ... )
        """
        if self._scope_provider is None:
            # Fallback if scope provider not configured
            return self._build_scope_fallback_response(query, collection)
        
        try:
            # Get scope information
            scope = self._scope_provider.get_collection_scope(collection)
            
            # Format scope response
            content = self._scope_provider.format_scope_response(scope, query)
            
            # Build metadata
            metadata = {
                "query": query,
                "scope_query": True,
                "collection": scope.collection,
                "document_count": scope.document_count,
                "document_types": sorted(list(scope.document_types)),
            }
            
            return MCPToolResponse(
                content=content,
                citations=[],
                metadata=metadata,
                is_empty=False,
                image_contents=[],
            )
        
        except Exception as e:
            logger.error(f"Failed to build scope response: {e}")
            return self._build_scope_fallback_response(query, collection)
    
    def _build_scope_fallback_response(
        self,
        query: str,
        collection: Optional[str],
    ) -> MCPToolResponse:
        """Build a fallback scope response when scope provider is unavailable.
        
        Args:
            query: User query
            collection: Collection name
            
        Returns:
            MCPToolResponse with basic scope information
        """
        lines = [
            "## 知识库范围说明",
            "",
            f"针对查询 **\"{query}\"**，当前知识库包含以下类型的文档：",
            "",
            "### 文档类型",
            "",
            "- 指南文档 (Guidelines)",
            "- 标准操作程序 (SOP)",
            "- 设备说明书 (Manuals)",
            "- 培训材料 (Training Materials)",
            "",
            "### 使用建议",
            "",
            "**适合查询的问题类型：**",
            "- 规范和指南的具体内容",
            "- 标准操作程序的步骤",
            "- 设备操作和维护说明",
            "- 培训材料和质量控制流程",
            "",
            "**不适合的问题类型：**",
            "- 诊断性或预测性问题",
            "- 超出当前文档范围的内容",
            "",
        ]
        
        if collection:
            lines.extend([
                "---",
                "",
                f"**集合名称:** `{collection}`",
                "",
            ])
        
        metadata = {
            "query": query,
            "scope_query": True,
            "fallback": True,
        }
        
        if collection:
            metadata["collection"] = collection
        
        return MCPToolResponse(
            content="\n".join(lines),
            citations=[],
            metadata=metadata,
            is_empty=False,
            image_contents=[],
        )

