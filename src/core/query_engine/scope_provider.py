"""Knowledge base scope awareness provider.

This module provides functionality to query and describe the current
knowledge base scope, including document types, counts, and coverage areas.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class ScopeInfo:
    """Information about knowledge base scope.
    
    Attributes:
        collection: Collection name
        document_types: Set of document types present (guideline, sop, manual, training)
        document_count: Total number of documents
        chunk_count: Total number of chunks
        last_updated: Timestamp of last update (ISO format)
        document_list: Optional list of document names
        coverage_areas: Optional list of coverage areas/topics
    """
    
    collection: str
    document_types: Set[str] = field(default_factory=set)
    document_count: int = 0
    chunk_count: int = 0
    last_updated: Optional[str] = None
    document_list: List[str] = field(default_factory=list)
    coverage_areas: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "collection": self.collection,
            "document_types": sorted(list(self.document_types)),
            "document_count": self.document_count,
            "chunk_count": self.chunk_count,
            "last_updated": self.last_updated,
            "document_list": self.document_list,
            "coverage_areas": self.coverage_areas,
        }


class ScopeProvider:
    """Provide knowledge base scope information.
    
    This class queries collection metadata to provide accurate information
    about what the system knows, including document types, counts, and
    coverage areas.
    
    Design Principles:
    - Dynamic: Reflects current collection state without hardcoding
    - Accurate: Only reports what actually exists in the collection
    - Informative: Provides enough detail for users to formulate queries
    
    Example:
        >>> provider = ScopeProvider(document_manager=doc_mgr)
        >>> scope = provider.get_collection_scope("medical_demo_v01")
        >>> response = provider.format_scope_response(scope)
    """
    
    # Document type detection patterns (medical domain)
    _DOC_TYPE_PATTERNS = {
        "guideline": ["guideline", "指南", "guide"],
        "sop": ["sop", "标准操作程序", "procedure"],
        "manual": ["manual", "说明书", "user_manual", "使用手册"],
        "training": ["training", "培训", "教程", "tutorial"],
    }
    
    # Autonomous driving document type detection patterns
    _AD_DOC_TYPE_PATTERNS = {
        "sensor_doc": [
            "sensor_doc", "sensor_spec", "lidar_spec", "camera_spec", "radar_spec",
            "ultrasonic_spec", "calibration_doc", "传感器规格", "激光雷达规格",
            "摄像头规格", "毫米波雷达规格", "超声波规格", "标定文档",
        ],
        "algorithm_doc": [
            "algorithm_doc", "perception_design", "planning_design", "control_design",
            "slam_doc", "detection_algorithm", "trajectory_algorithm",
            "算法设计", "感知设计", "规划设计", "控制设计",
        ],
        "regulation_doc": [
            "regulation_doc", "gb_t_", "iso_26262", "asil_", "functional_safety_doc",
            "test_specification", "法规文档", "国家标准", "功能安全文档", "测试规范文档",
        ],
        "test_doc": [
            "test_doc", "test_scenario", "test_case", "test_report",
            "functional_test", "safety_test", "boundary_test",
            "测试文档", "测试场景", "测试用例", "测试报告",
        ],
    }
    
    # AD coverage area keywords
    _AD_COVERAGE_KEYWORDS = {
        "sensor": "传感器技术",
        "camera": "摄像头",
        "lidar": "激光雷达",
        "radar": "毫米波雷达",
        "ultrasonic": "超声波雷达",
        "perception": "感知算法",
        "planning": "规划算法",
        "control": "控制算法",
        "slam": "SLAM算法",
        "regulation": "法规标准",
        "iso": "ISO标准",
        "gb": "国家标准",
        "test": "测试场景",
        "scenario": "测试场景",
        "safety": "安全测试",
        "calibration": "传感器标定",
    }
    
    def __init__(
        self,
        document_manager: Any,
    ) -> None:
        """Initialize ScopeProvider.
        
        Args:
            document_manager: DocumentManager instance for querying collection metadata
        """
        self.document_manager = document_manager
    
    def get_collection_scope(
        self,
        collection: Optional[str] = None,
    ) -> ScopeInfo:
        """Query collection metadata to get scope information.
        
        This method queries the document manager to get accurate information
        about the current collection state, including document types, counts,
        and last update timestamp.
        
        Args:
            collection: Collection name (optional, uses default if None)
            
        Returns:
            ScopeInfo with current collection metadata
            
        Example:
            >>> scope = provider.get_collection_scope("medical_demo_v01")
            >>> print(f"Collection has {scope.document_count} documents")
            >>> print(f"Document types: {scope.document_types}")
        """
        # Get collection statistics
        stats = self.document_manager.get_collection_stats(collection)
        
        # Get document list
        documents = self.document_manager.list_documents(collection)
        
        # Extract document types from document names
        document_types: Set[str] = set()
        document_list: List[str] = []
        
        for doc in documents:
            # Add to document list
            document_list.append(doc.source_path)
            
            # Detect document type from path
            doc_type = self._detect_document_type(doc.source_path)
            if doc_type:
                document_types.add(doc_type)
        
        # Get last updated timestamp (most recent processed_at)
        last_updated = None
        if documents:
            # Find most recent processed_at timestamp
            timestamps = [
                doc.processed_at for doc in documents 
                if doc.processed_at is not None
            ]
            if timestamps:
                # Sort and get most recent
                timestamps.sort(reverse=True)
                last_updated = timestamps[0]
        
        # If no timestamp found, use current time
        if last_updated is None:
            last_updated = datetime.now().isoformat()
        
        # Extract coverage areas from document names
        coverage_areas = self._extract_coverage_areas(document_list)
        
        return ScopeInfo(
            collection=collection or "default",
            document_types=document_types,
            document_count=stats.document_count,
            chunk_count=stats.chunk_count,
            last_updated=last_updated,
            document_list=document_list,
            coverage_areas=coverage_areas,
        )
    
    def format_scope_response(
        self,
        scope: ScopeInfo,
        query: Optional[str] = None,
    ) -> str:
        """Format scope information as a user-friendly response.
        
        This method creates a structured response describing the knowledge
        base scope, including document types, counts, and coverage areas.
        
        Args:
            scope: ScopeInfo object with collection metadata
            query: Optional user query for context
            
        Returns:
            Formatted markdown response describing the scope
            
        Example:
            >>> scope = provider.get_collection_scope("medical_demo_v01")
            >>> response = provider.format_scope_response(scope)
            >>> print(response)
        """
        lines = [
            "## 知识库范围说明",
            "",
        ]
        
        # Add query context if provided
        if query:
            lines.extend([
                f"针对查询 **\"{query}\"**，以下是当前知识库的覆盖范围：",
                "",
            ])
        else:
            lines.extend([
                "当前知识库的覆盖范围如下：",
                "",
            ])
        
        # Document types section
        if scope.document_types:
            lines.extend([
                "### 文档类型",
                "",
            ])
            
            doc_type_names = {
                "guideline": "指南文档",
                "sop": "标准操作程序 (SOP)",
                "manual": "设备说明书",
                "training": "培训材料",
            }
            
            for doc_type in sorted(scope.document_types):
                type_name = doc_type_names.get(doc_type, doc_type)
                lines.append(f"- {type_name}")
            
            lines.append("")
        
        # Coverage areas section
        if scope.coverage_areas:
            lines.extend([
                "### 覆盖领域",
                "",
            ])
            
            for area in scope.coverage_areas[:10]:  # Limit to top 10
                lines.append(f"- {area}")
            
            if len(scope.coverage_areas) > 10:
                lines.append(f"- ...以及其他 {len(scope.coverage_areas) - 10} 个领域")
            
            lines.append("")
        
        # Statistics section
        lines.extend([
            "### 统计信息",
            "",
            f"- **文档总数:** {scope.document_count}",
            f"- **知识片段数:** {scope.chunk_count}",
            f"- **最后更新:** {self._format_timestamp(scope.last_updated)}",
            "",
        ])
        
        # Usage guidance
        lines.extend([
            "### 使用建议",
            "",
            "**适合查询的问题类型：**",
            "- 规范和指南的具体内容",
            "- 标准操作程序 (SOP) 的步骤",
            "- 设备操作和维护说明",
            "- 培训材料和质量控制流程",
            "",
            "**不适合的问题类型：**",
            "- 诊断性或预测性问题",
            "- 超出当前文档范围的内容",
            "- 需要实时数据或最新研究的问题",
            "",
        ])
        
        # Collection info
        lines.extend([
            "---",
            "",
            f"**集合名称:** `{scope.collection}`",
            "",
        ])
        
        return "\n".join(lines)
    
    def _detect_document_type(
        self,
        document_path: str,
    ) -> Optional[str]:
        """Detect document type from file path.
        
        Supports both medical domain and autonomous driving domain types.
        
        Args:
            document_path: Document file path
            
        Returns:
            Document type string or None if not detected
        """
        path_lower = document_path.lower()
        
        # Check medical domain types first (backward compatibility)
        for doc_type, patterns in self._DOC_TYPE_PATTERNS.items():
            for pattern in patterns:
                if pattern in path_lower:
                    return doc_type
        
        # Then check AD document types
        for doc_type, patterns in self._AD_DOC_TYPE_PATTERNS.items():
            for pattern in patterns:
                if pattern in path_lower:
                    return doc_type
        
        return None
    
    def get_document_statistics(
        self,
        collection: Optional[str] = None,
    ) -> Dict[str, int]:
        """Get document count statistics by type.
        
        Returns counts for each document type present in the collection.
        Supports both medical and autonomous driving document types.
        
        Args:
            collection: Collection name (optional)
            
        Returns:
            Dict mapping document type to count, e.g.:
            {"sensor_doc": 50, "algorithm_doc": 80, "regulation_doc": 30, "test_doc": 100}
        """
        documents = self.document_manager.list_documents(collection)
        
        stats: Dict[str, int] = {}
        for doc in documents:
            doc_type = self._detect_document_type(doc.source_path)
            if doc_type:
                stats[doc_type] = stats.get(doc_type, 0) + 1
        
        return stats
    
    def format_ad_scope_response(
        self,
        scope: ScopeInfo,
        statistics: Optional[Dict[str, int]] = None,
        query: Optional[str] = None,
    ) -> str:
        """Format scope information for autonomous driving knowledge base.
        
        Args:
            scope: ScopeInfo object with collection metadata
            statistics: Optional per-type document counts
            query: Optional user query for context
            
        Returns:
            Formatted markdown response for AD domain
        """
        lines = [
            "## 知识库范围",
            "",
        ]
        
        if query:
            lines.extend([
                f"针对查询 **\"{query}\"**，以下是当前知识库的覆盖范围：",
                "",
            ])
        
        # Collection name
        lines.extend([
            f"当前知识库 **{scope.collection}** 包含以下内容：",
            "",
        ])
        
        # Document types with counts
        ad_type_names = {
            "sensor_doc": "传感器文档",
            "algorithm_doc": "算法文档",
            "regulation_doc": "法规文档",
            "test_doc": "测试文档",
        }
        
        ad_type_descriptions = {
            "sensor_doc": "摄像头、激光雷达、毫米波雷达、超声波雷达的规格书和标定文档",
            "algorithm_doc": "感知算法、规划算法、控制算法的设计文档和技术报告",
            "regulation_doc": "GB/T 国家标准、ISO 26262 功能安全标准、测试规范",
            "test_doc": "测试场景库、测试用例、测试报告",
        }
        
        lines.extend(["**文档类型:**", ""])
        
        ad_types_present = [t for t in ad_type_names if t in scope.document_types]
        if ad_types_present:
            for doc_type in ad_types_present:
                count = statistics.get(doc_type, 0) if statistics else 0
                name = ad_type_names[doc_type]
                desc = ad_type_descriptions.get(doc_type, "")
                count_str = f" ({count} 份)" if count > 0 else ""
                lines.append(f"- {name}{count_str}: {desc}")
        else:
            # Show all AD types as available
            for doc_type, name in ad_type_names.items():
                desc = ad_type_descriptions.get(doc_type, "")
                lines.append(f"- {name}: {desc}")
        
        lines.append("")
        
        # Coverage areas
        if scope.coverage_areas:
            lines.extend(["**覆盖领域:**", ""])
            for area in scope.coverage_areas[:8]:
                lines.append(f"- {area}")
            lines.append("")
        
        # Statistics
        lines.extend([
            f"**最后更新:** {self._format_timestamp(scope.last_updated)}",
            f"**总文档数:** {scope.document_count} 份",
            f"**总 Chunk 数:** {scope.chunk_count}+",
            "",
        ])
        
        return "\n".join(lines)
    
    def _extract_coverage_areas(
        self,
        document_list: List[str],
    ) -> List[str]:
        """Extract coverage areas from document names.
        
        Supports both medical and autonomous driving domain keywords.
        
        Args:
            document_list: List of document paths
            
        Returns:
            List of coverage area strings
        """
        coverage_areas: Set[str] = set()
        
        # Medical domain keywords
        medical_keywords = {
            "transport": "样本运输",
            "quality": "质量管理",
            "sample": "样本管理",
            "equipment": "设备管理",
            "safety": "安全管理",
            "training": "培训",
            "sop": "标准操作程序",
            "guideline": "指南规范",
            "manual": "设备说明",
            "lab": "实验室",
            "pathology": "病理",
            "histology": "组织学",
            "specimen": "标本",
            "tissue": "组织",
            "processing": "处理流程",
            "staining": "染色",
            "microscopy": "显微镜",
            "documentation": "文档记录",
            "records": "记录管理",
        }
        
        for doc_path in document_list:
            path_lower = doc_path.lower()
            
            # Check AD keywords first
            for keyword, area_name in self._AD_COVERAGE_KEYWORDS.items():
                if keyword in path_lower:
                    coverage_areas.add(area_name)
            
            # Check medical keywords
            for keyword, area_name in medical_keywords.items():
                if keyword in path_lower:
                    coverage_areas.add(area_name)
        
        return sorted(list(coverage_areas))
    
    def _format_timestamp(
        self,
        timestamp: Optional[str],
    ) -> str:
        """Format timestamp for display.
        
        Args:
            timestamp: ISO format timestamp string
            
        Returns:
            Formatted timestamp string
        """
        if not timestamp:
            return "未知"
        
        try:
            # Parse ISO format timestamp
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            # Format as readable Chinese date
            return dt.strftime("%Y年%m月%d日 %H:%M")
        except Exception:
            # Return original if parsing fails
            return timestamp
