"""Metadata Booster for Autonomous Driving Knowledge Retrieval.

This module implements metadata-based score boosting to prioritize certain
document types based on query characteristics. For example, sensor queries
should prioritize sensor_doc type documents.

Design Principles:
- Query Type Detection: Identify query intent (sensor, algorithm, regulation, test)
- Configurable Boost Weights: Apply different weights based on query type
- Top-K Verification: Ensure target document types appear in top results
- Fallback Mechanism: Use standard retrieval if boost fails
- Observable: Log boost application for analysis
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.core.types import RetrievalResult

logger = logging.getLogger(__name__)


@dataclass
class MetadataBoostResult:
    """Result of metadata boost application.
    
    Attributes:
        original_chunks: Original retrieval results before boost
        boosted_chunks: Results after applying boost weights
        boost_applied: Whether boost was successfully applied
        boost_type: Type of boost applied (sensor_query, algorithm_query, etc.)
        boost_config: Boost weights used
        top_k_verified: Whether top-K verification passed
        fallback_used: Whether fallback to standard retrieval was used
    """
    original_chunks: List[RetrievalResult] = field(default_factory=list)
    boosted_chunks: List[RetrievalResult] = field(default_factory=list)
    boost_applied: bool = False
    boost_type: Optional[str] = None
    boost_config: Dict[str, float] = field(default_factory=dict)
    top_k_verified: bool = False
    fallback_used: bool = False


class MetadataBooster:
    """Metadata-based score booster for autonomous driving queries.
    
    This class detects query types (sensor, algorithm, regulation, test) and
    applies configurable boost weights to prioritize relevant document types.
    
    Example:
        >>> booster = MetadataBooster(boost_config={
        ...     "sensor_query": {"sensor_doc": 1.5, "algorithm_doc": 0.8},
        ...     "algorithm_query": {"algorithm_doc": 1.3, "sensor_doc": 0.9}
        ... })
        >>> 
        >>> # Detect query type
        >>> query_type = booster.detect_query_type("激光雷达的探测距离是多少？")
        >>> # query_type = "sensor_query"
        >>> 
        >>> # Apply boost
        >>> boosted = booster.apply_boost(chunks, query_type)
    """
    
    # Query type detection patterns
    SENSOR_PATTERNS = [
        r"摄像头", r"camera", r"相机",
        r"激光雷达", r"lidar",
        r"毫米波雷达", r"radar", r"雷达",
        r"超声波", r"ultrasonic",
        r"分辨率", r"resolution",
        r"帧率", r"frame\s*rate", r"fps",
        r"视场角", r"fov", r"field\s*of\s*view",
        r"探测距离", r"detection\s*range", r"range",
        r"标定", r"calibration",
        r"内参", r"intrinsic",
        r"外参", r"extrinsic",
    ]
    
    ALGORITHM_PATTERNS = [
        r"感知", r"perception",
        r"规划", r"planning",
        r"控制", r"control",
        r"slam",
        r"目标检测", r"object\s*detection",
        r"车道线", r"lane",
        r"障碍物", r"obstacle",
        r"路径规划", r"path\s*planning",
        r"轨迹", r"trajectory",
        r"pid", r"mpc",
        r"算法", r"algorithm",
    ]
    
    REGULATION_PATTERNS = [
        r"gb/t", r"gb\s*\d+",
        r"iso\s*26262", r"iso",
        r"标准", r"standard",
        r"法规", r"regulation",
        r"asil",
        r"功能安全", r"functional\s*safety",
        r"测试规范", r"test\s*specification",
        r"测试规程", r"test\s*procedure",
    ]
    
    TEST_PATTERNS = [
        r"测试", r"test",
        r"场景", r"scenario",
        r"用例", r"case",
        r"跟车", r"following",
        r"变道", r"lane\s*change",
        r"超车", r"overtaking",
        r"紧急制动", r"emergency\s*braking",
        r"功能测试", r"functional\s*test",
        r"安全测试", r"safety\s*test",
    ]
    
    def __init__(
        self,
        boost_config: Optional[Dict[str, Dict[str, float]]] = None,
        top_k_threshold: int = 3,
        top_k_min_count: int = 2,
    ) -> None:
        """Initialize MetadataBooster.
        
        Args:
            boost_config: Boost weight configuration. Format:
                {
                    "sensor_query": {"sensor_doc": 1.5, "algorithm_doc": 0.8},
                    "algorithm_query": {"algorithm_doc": 1.3, "sensor_doc": 0.9},
                    ...
                }
            top_k_threshold: Number of top results to verify (default: 3)
            top_k_min_count: Minimum count of target doc type in top-K (default: 2)
        """
        self.boost_config = boost_config or self._default_boost_config()
        self.top_k_threshold = top_k_threshold
        self.top_k_min_count = top_k_min_count
        
        logger.info(
            f"MetadataBooster initialized with {len(self.boost_config)} query types, "
            f"top_k_threshold={top_k_threshold}, top_k_min_count={top_k_min_count}"
        )
    
    def _default_boost_config(self) -> Dict[str, Dict[str, float]]:
        """Get default boost configuration.
        
        Returns:
            Default boost weights for each query type.
        """
        return {
            "sensor_query": {
                "sensor_doc": 1.5,
                "algorithm_doc": 0.8,
                "regulation_doc": 0.9,
                "test_doc": 0.9,
            },
            "algorithm_query": {
                "algorithm_doc": 1.3,
                "sensor_doc": 0.9,
                "regulation_doc": 0.9,
                "test_doc": 0.9,
            },
            "regulation_query": {
                "regulation_doc": 1.6,
                "test_doc": 1.2,
                "sensor_doc": 0.8,
                "algorithm_doc": 0.8,
            },
            "test_query": {
                "test_doc": 1.4,
                "regulation_doc": 1.1,
                "sensor_doc": 0.9,
                "algorithm_doc": 0.9,
            },
        }
    
    def detect_query_type(self, query: str) -> str:
        """Detect query type based on keywords.
        
        Args:
            query: User query string.
            
        Returns:
            Query type: "sensor_query", "algorithm_query", "regulation_query",
            "test_query", or "general" if no specific type detected.
        """
        if not query:
            return "general"
        
        query_lower = query.lower()
        
        # Count matches for each pattern type
        sensor_matches = sum(
            1 for pattern in self.SENSOR_PATTERNS
            if re.search(pattern, query_lower, re.IGNORECASE)
        )
        algorithm_matches = sum(
            1 for pattern in self.ALGORITHM_PATTERNS
            if re.search(pattern, query_lower, re.IGNORECASE)
        )
        regulation_matches = sum(
            1 for pattern in self.REGULATION_PATTERNS
            if re.search(pattern, query_lower, re.IGNORECASE)
        )
        test_matches = sum(
            1 for pattern in self.TEST_PATTERNS
            if re.search(pattern, query_lower, re.IGNORECASE)
        )
        
        # Determine query type based on highest match count
        match_counts = {
            "sensor_query": sensor_matches,
            "algorithm_query": algorithm_matches,
            "regulation_query": regulation_matches,
            "test_query": test_matches,
        }
        
        max_matches = max(match_counts.values())
        if max_matches == 0:
            return "general"
        
        # Return the query type with highest match count
        query_type = max(match_counts, key=match_counts.get)
        
        logger.debug(
            f"Query type detected: {query_type} "
            f"(sensor={sensor_matches}, algorithm={algorithm_matches}, "
            f"regulation={regulation_matches}, test={test_matches})"
        )
        
        return query_type
    
    def apply_boost(
        self,
        chunks: List[RetrievalResult],
        query: str,
        trace: Optional[Any] = None,
    ) -> List[RetrievalResult]:
        """Apply metadata boost to retrieval results.
        
        Args:
            chunks: Original retrieval results.
            query: User query string (for query type detection).
            trace: Optional TraceContext for observability.
            
        Returns:
            Boosted and re-sorted retrieval results.
        """
        if not chunks:
            return chunks
        
        # Detect query type
        query_type = self.detect_query_type(query)
        
        if query_type == "general":
            logger.debug("General query detected, no boost applied")
            return chunks
        
        # Get boost config for this query type
        boost_weights = self.boost_config.get(query_type, {})
        if not boost_weights:
            logger.warning(f"No boost config for query type: {query_type}")
            return chunks
        
        # Apply boost weights
        boosted_chunks = []
        for chunk in chunks:
            doc_type = chunk.metadata.get("doc_type", "unknown")
            boost_weight = boost_weights.get(doc_type, 1.0)
            
            # Create new RetrievalResult with boosted score
            boosted_chunk = RetrievalResult(
                chunk_id=chunk.chunk_id,
                score=chunk.score * boost_weight,
                text=chunk.text,
                metadata=chunk.metadata.copy(),
            )
            boosted_chunks.append(boosted_chunk)
        
        # Re-sort by boosted scores
        boosted_chunks.sort(key=lambda x: x.score, reverse=True)
        
        # Verify top-K results
        top_k_verified = self._verify_top_k(
            boosted_chunks, query_type, boost_weights
        )
        
        # Log boost application
        if trace is not None:
            trace.record_stage("metadata_boost", {
                "query_type": query_type,
                "boost_weights": boost_weights,
                "top_k_verified": top_k_verified,
                "original_top_3": [
                    {"chunk_id": c.chunk_id, "score": c.score, "doc_type": c.metadata.get("doc_type")}
                    for c in chunks[:3]
                ],
                "boosted_top_3": [
                    {"chunk_id": c.chunk_id, "score": c.score, "doc_type": c.metadata.get("doc_type")}
                    for c in boosted_chunks[:3]
                ],
            })
        
        logger.info(
            f"Metadata boost applied: query_type={query_type}, "
            f"top_k_verified={top_k_verified}, "
            f"chunks_count={len(boosted_chunks)}"
        )
        
        return boosted_chunks
    
    def _verify_top_k(
        self,
        chunks: List[RetrievalResult],
        query_type: str,
        boost_weights: Dict[str, float],
    ) -> bool:
        """Verify that top-K results contain expected document types.
        
        Args:
            chunks: Boosted retrieval results (sorted by score).
            query_type: Detected query type.
            boost_weights: Boost weights used.
            
        Returns:
            True if top-K verification passed, False otherwise.
        """
        if len(chunks) < self.top_k_threshold:
            # Not enough chunks to verify
            return True
        
        # Get target document type (the one with highest boost weight)
        target_doc_type = max(boost_weights, key=boost_weights.get)
        
        # Count target doc type in top-K
        top_k_chunks = chunks[:self.top_k_threshold]
        target_count = sum(
            1 for chunk in top_k_chunks
            if chunk.metadata.get("doc_type") == target_doc_type
        )
        
        verified = target_count >= self.top_k_min_count
        
        if not verified:
            logger.warning(
                f"Top-K verification failed: query_type={query_type}, "
                f"target_doc_type={target_doc_type}, "
                f"target_count={target_count}/{self.top_k_min_count}"
            )
        
        return verified
    
    def apply_boost_with_details(
        self,
        chunks: List[RetrievalResult],
        query: str,
        trace: Optional[Any] = None,
    ) -> MetadataBoostResult:
        """Apply boost and return detailed result.
        
        Args:
            chunks: Original retrieval results.
            query: User query string.
            trace: Optional TraceContext.
            
        Returns:
            MetadataBoostResult with detailed information.
        """
        query_type = self.detect_query_type(query)
        boost_weights = self.boost_config.get(query_type, {})
        
        if query_type == "general" or not boost_weights:
            return MetadataBoostResult(
                original_chunks=chunks,
                boosted_chunks=chunks,
                boost_applied=False,
                boost_type=query_type,
                boost_config={},
                top_k_verified=True,
                fallback_used=False,
            )
        
        boosted_chunks = self.apply_boost(chunks, query, trace)
        top_k_verified = self._verify_top_k(boosted_chunks, query_type, boost_weights)
        
        # Use fallback if verification failed
        fallback_used = False
        if not top_k_verified:
            logger.warning("Top-K verification failed, using fallback (original results)")
            boosted_chunks = chunks
            fallback_used = True
        
        return MetadataBoostResult(
            original_chunks=chunks,
            boosted_chunks=boosted_chunks,
            boost_applied=not fallback_used,
            boost_type=query_type,
            boost_config=boost_weights,
            top_k_verified=top_k_verified,
            fallback_used=fallback_used,
        )
