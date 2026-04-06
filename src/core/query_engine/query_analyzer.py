"""Query Analyzer for detecting query complexity and intent.

This module provides query analysis functionality to route queries to appropriate
processing pipelines based on their complexity and intent.

Design Principles:
- Pattern-based detection: Use keyword patterns for reliable classification
- Chinese medical domain: Optimized for Chinese medical queries
- Multi-dimensional analysis: Detect both complexity and intent
- Extensible: Easy to add new patterns and classifications
"""

import re
from dataclasses import dataclass, field
from typing import List, Literal, Set

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


# Complexity detection patterns
COMPARISON_KEYWORDS: Set[str] = {
    "不同", "区别", "差异", "对比", "比较", "相比", "异同",
    "vs", "versus", "对照", "差别"
}

AGGREGATION_KEYWORDS: Set[str] = {
    "哪些", "总结", "汇总", "归纳", "概括", "列举", "所有",
    "全部", "整理", "梳理", "综述"
}

MULTI_PART_INDICATORS: Set[str] = {
    "以及", "还有", "另外", "此外", "同时", "并且", "而且",
    "和", "与", "及"
}

# Intent detection patterns
BOUNDARY_KEYWORDS: Set[str] = {
    # Predictive patterns
    "预测", "预计", "预期", "预判", "预估", "预报",
    "下个月", "下周", "下季度", "下年", "未来", "将来",
    "最常见", "最可能", "会发生", "可能性", "概率",
    # Diagnostic patterns (existing from P0)
    "诊断", "判断", "确诊", "鉴别", "病因", "症状分析",
    "治疗方案", "用药建议", "处方", "医嘱"
}

SCOPE_KEYWORDS: Set[str] = {
    "覆盖", "包含", "范围", "知识库", "文档库", "数据库",
    "有哪些文档", "有什么资料", "支持哪些", "能查什么",
    "包括什么", "涵盖", "收录"
}


@dataclass
class QueryAnalysis:
    """Analysis result for a user query.
    
    Attributes:
        complexity: Query complexity level
            - simple: Single straightforward question
            - multi_part: Multiple sub-questions
            - comparison: Requires comparing multiple sources
            - aggregation: Requires synthesizing from multiple sources
        intent: Primary intent of the query
            - retrieval: Standard information retrieval
            - boundary: Query crosses system boundaries (diagnostic/predictive)
            - scope_inquiry: Asking about knowledge base scope
        sub_queries: List of sub-questions (for multi_part queries)
        requires_multi_doc: Whether query requires multiple documents
        detected_keywords: Keywords that triggered the classification
    """
    
    complexity: Literal["simple", "multi_part", "comparison", "aggregation"]
    intent: Literal["retrieval", "boundary", "scope_inquiry"]
    sub_queries: List[str] = field(default_factory=list)
    requires_multi_doc: bool = False
    detected_keywords: List[str] = field(default_factory=list)


class QueryAnalyzer:
    """Analyzes queries to determine complexity and intent.
    
    Uses keyword pattern matching optimized for Chinese medical queries
    to classify queries and route them to appropriate processing pipelines.
    
    Example:
        >>> analyzer = QueryAnalyzer()
        >>> analysis = analyzer.analyze("WHO运输指南和质量管理指南有什么不同？")
        >>> print(analysis.complexity)  # "comparison"
        >>> print(analysis.requires_multi_doc)  # True
    """
    
    def __init__(self):
        """Initialize QueryAnalyzer with default patterns."""
        self.comparison_keywords = COMPARISON_KEYWORDS
        self.aggregation_keywords = AGGREGATION_KEYWORDS
        self.multi_part_indicators = MULTI_PART_INDICATORS
        self.boundary_keywords = BOUNDARY_KEYWORDS
        self.scope_keywords = SCOPE_KEYWORDS
    
    def analyze(self, query: str) -> QueryAnalysis:
        """Analyze query to determine complexity and intent.
        
        Args:
            query: User query string
            
        Returns:
            QueryAnalysis with detected complexity, intent, and metadata
        """
        if not query or not query.strip():
            return QueryAnalysis(
                complexity="simple",
                intent="retrieval",
                sub_queries=[],
                requires_multi_doc=False,
                detected_keywords=[]
            )
        
        query_lower = query.lower()
        detected_keywords: List[str] = []
        
        # Detect intent first (higher priority)
        intent = self._detect_intent(query_lower, detected_keywords)
        
        # Detect complexity
        complexity = self._detect_complexity(query, query_lower, detected_keywords)
        
        # Determine if multi-document retrieval is needed
        requires_multi_doc = self._requires_multi_document(complexity, intent)
        
        # Extract sub-queries for multi-part queries
        sub_queries = self._extract_sub_queries(query) if complexity == "multi_part" else []
        
        return QueryAnalysis(
            complexity=complexity,
            intent=intent,
            sub_queries=sub_queries,
            requires_multi_doc=requires_multi_doc,
            detected_keywords=detected_keywords
        )
    
    def _detect_intent(self, query_lower: str, detected_keywords: List[str]) -> Literal["retrieval", "boundary", "scope_inquiry"]:
        """Detect the primary intent of the query.
        
        Args:
            query_lower: Lowercase query string
            detected_keywords: List to append detected keywords to
            
        Returns:
            Detected intent type
        """
        # Check for scope inquiry keywords
        for keyword in self.scope_keywords:
            if keyword in query_lower:
                detected_keywords.append(keyword)
                return "scope_inquiry"
        
        # Check for boundary keywords (diagnostic/predictive)
        for keyword in self.boundary_keywords:
            if keyword in query_lower:
                detected_keywords.append(keyword)
                return "boundary"
        
        # Default to retrieval
        return "retrieval"
    
    def _detect_complexity(
        self, 
        query: str, 
        query_lower: str, 
        detected_keywords: List[str]
    ) -> Literal["simple", "multi_part", "comparison", "aggregation"]:
        """Detect the complexity level of the query.
        
        Args:
            query: Original query string
            query_lower: Lowercase query string
            detected_keywords: List to append detected keywords to
            
        Returns:
            Detected complexity level
        """
        # Check for comparison keywords
        for keyword in self.comparison_keywords:
            if keyword in query_lower:
                detected_keywords.append(keyword)
                return "comparison"
        
        # Check for aggregation keywords
        for keyword in self.aggregation_keywords:
            if keyword in query_lower:
                detected_keywords.append(keyword)
                return "aggregation"
        
        # Check for multi-part indicators
        multi_part_count = 0
        for indicator in self.multi_part_indicators:
            if indicator in query_lower:
                multi_part_count += 1
                detected_keywords.append(indicator)
        
        # Check for multiple question marks
        question_marks = query.count("？") + query.count("?")
        
        # Classify as multi_part if multiple indicators or questions
        if multi_part_count >= 2 or question_marks >= 2:
            return "multi_part"
        
        # Default to simple
        return "simple"
    
    def _requires_multi_document(
        self, 
        complexity: str, 
        intent: str
    ) -> bool:
        """Determine if query requires multi-document retrieval.
        
        Args:
            complexity: Detected complexity level
            intent: Detected intent
            
        Returns:
            True if multi-document retrieval is needed
        """
        # Scope inquiries don't need document retrieval (check first)
        if intent == "scope_inquiry":
            return False
        
        # Comparison and aggregation always need multiple documents
        if complexity in ("comparison", "aggregation"):
            return True
        
        # Multi-part queries may need multiple documents
        if complexity == "multi_part":
            return True
        
        # Simple retrieval queries default to single document
        return False
    
    def _extract_sub_queries(self, query: str) -> List[str]:
        """Extract sub-questions from a multi-part query.
        
        Args:
            query: Original query string
            
        Returns:
            List of sub-questions
        """
        sub_queries: List[str] = []
        
        # Split by question marks
        parts = re.split(r'[？?]', query)
        for part in parts:
            part = part.strip()
            if part:
                # Add question mark back
                sub_queries.append(part + "？")
        
        # If no question marks, try splitting by multi-part indicators
        if len(sub_queries) <= 1:
            # Try splitting by common conjunctions
            for indicator in ["以及", "还有", "另外", "此外", "同时"]:
                if indicator in query:
                    parts = query.split(indicator)
                    sub_queries = [p.strip() for p in parts if p.strip()]
                    break
        
        # Return original query if no splits found
        if len(sub_queries) <= 1:
            return [query]
        
        return sub_queries


def create_query_analyzer() -> QueryAnalyzer:
    """Factory function to create QueryAnalyzer.
    
    Returns:
        Configured QueryAnalyzer instance
    """
    return QueryAnalyzer()
