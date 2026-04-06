"""
Response Module.

This package contains response building components:
- Response builder
- Citation generator
- Citation enhancer
- Multimodal assembler
"""

from src.core.response.citation_enhancer import CitationEnhancer, EnhancedCitation
from src.core.response.citation_generator import Citation, CitationGenerator
from src.core.response.multimodal_assembler import (
    ImageContent,
    ImageReference,
    MultimodalAssembler,
)
from src.core.response.response_builder import MCPToolResponse, ResponseBuilder

__all__ = [
    "Citation",
    "CitationEnhancer",
    "CitationGenerator",
    "EnhancedCitation",
    "ImageContent",
    "ImageReference",
    "MCPToolResponse",
    "MultimodalAssembler",
    "ResponseBuilder",
]
