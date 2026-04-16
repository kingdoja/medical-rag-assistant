"""Autonomous Driving Metadata Tagger.

This module provides automatic metadata tagging for autonomous driving documents
based on their location and filename patterns. It supports four document types:
- sensor_doc: Camera, LiDAR, Radar, Ultrasonic sensor documents
- algorithm_doc: Perception, Planning, Control algorithm documents
- regulation_doc: GB/T, ISO 26262, test specifications
- test_doc: Functional, Safety, Boundary test documents

The tagger integrates with the ingestion pipeline to automatically apply
metadata tags during document ingestion.
"""

import re
from pathlib import Path
from typing import Dict, Optional, Any, List
from dataclasses import dataclass

from src.observability.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DocumentMetadata:
    """Metadata for an autonomous driving document."""
    
    document_type: str  # sensor_doc, algorithm_doc, regulation_doc, test_doc
    # Type-specific fields (populated based on document_type)
    sensor_type: Optional[str] = None  # camera, lidar, radar, ultrasonic
    content_type: Optional[str] = None  # specification, calibration, installation, maintenance
    algorithm_type: Optional[str] = None  # perception, planning, control, slam
    algorithm_category: Optional[str] = None  # specific algorithm category
    regulation_type: Optional[str] = None  # national_standard, iso_standard, test_spec, industry_standard
    standard_number: Optional[str] = None  # GB/T, ISO 26262, etc.
    test_type: Optional[str] = None  # functional, safety, boundary, performance, simulation, real_vehicle
    test_category: Optional[str] = None  # specific test category
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        result = {"document_type": self.document_type}
        
        if self.sensor_type:
            result["sensor_type"] = self.sensor_type
        if self.content_type:
            result["content_type"] = self.content_type
        if self.algorithm_type:
            result["algorithm_type"] = self.algorithm_type
        if self.algorithm_category:
            result["algorithm_category"] = self.algorithm_category
        if self.regulation_type:
            result["regulation_type"] = self.regulation_type
        if self.standard_number:
            result["standard_number"] = self.standard_number
        if self.test_type:
            result["test_type"] = self.test_type
        if self.test_category:
            result["test_category"] = self.test_category
        
        return result


class ADMetadataTagger:
    """Automatic metadata tagger for autonomous driving documents.
    
    This class analyzes document paths and filenames to automatically assign
    appropriate metadata tags based on predefined patterns.
    
    Example:
        >>> tagger = ADMetadataTagger()
        >>> metadata = tagger.tag_document("demo-data-ad/sensors/camera/spec.pdf")
        >>> print(metadata.document_type)  # "sensor_doc"
        >>> print(metadata.sensor_type)    # "camera"
    """
    
    # Sensor type patterns
    SENSOR_PATTERNS = {
        "camera": [
            r"camera", r"摄像头", r"相机", r"视觉传感器",
            r"image_sensor", r"vision"
        ],
        "lidar": [
            r"lidar", r"激光雷达", r"laser", r"点云",
            r"velodyne", r"hesai", r"robosense"
        ],
        "radar": [
            r"radar", r"毫米波", r"雷达", r"mmwave",
            r"continental", r"bosch_radar"
        ],
        "ultrasonic": [
            r"ultrasonic", r"超声波", r"uss", r"parking_sensor"
        ]
    }
    
    # Content type patterns
    CONTENT_PATTERNS = {
        "specification": [r"spec", r"规格", r"datasheet", r"参数"],
        "calibration": [r"calib", r"标定", r"intrinsic", r"extrinsic"],
        "installation": [r"install", r"安装", r"mount", r"部署"],
        "maintenance": [r"maintain", r"维护", r"service", r"保养"]
    }
    
    # Algorithm type patterns
    ALGORITHM_PATTERNS = {
        "perception": [
            r"perception", r"感知", r"detect", r"检测",
            r"recognition", r"识别", r"segmentation", r"分割",
            r"tracking", r"跟踪", r"yolo", r"rcnn"
        ],
        "planning": [
            r"planning", r"规划", r"path", r"路径",
            r"trajectory", r"轨迹", r"behavior", r"行为",
            r"decision", r"决策", r"motion"
        ],
        "control": [
            r"control", r"控制", r"pid", r"mpc",
            r"lateral", r"横向", r"longitudinal", r"纵向",
            r"steering", r"转向", r"throttle", r"油门"
        ],
        "slam": [
            r"slam", r"localization", r"定位", r"mapping", r"建图"
        ]
    }
    
    # Regulation type patterns
    REGULATION_PATTERNS = {
        "national_standard": [r"gb/?t", r"国标", r"国家标准", r"gb_"],
        "iso_standard": [r"iso", r"国际标准"],
        "test_spec": [r"test.*spec", r"测试规范", r"test.*standard"],
        "industry_standard": [r"industry", r"行业标准", r"sae"]
    }
    
    # Test type patterns
    TEST_PATTERNS = {
        "functional": [r"functional", r"功能测试", r"function_test"],
        "safety": [r"safety", r"安全测试", r"safety_test", r"collision"],
        "boundary": [r"boundary", r"边界", r"edge_case", r"corner_case"],
        "performance": [r"performance", r"性能", r"benchmark"],
        "simulation": [r"simulation", r"仿真", r"sim", r"carla"],
        "real_vehicle": [r"real.*vehicle", r"实车", r"road_test", r"路测"]
    }
    
    def __init__(self):
        """Initialize the metadata tagger."""
        logger.info("ADMetadataTagger initialized")
    
    def tag_document(self, file_path: str) -> Optional[DocumentMetadata]:
        """Tag a document based on its path and filename.
        
        Args:
            file_path: Path to the document file
        
        Returns:
            DocumentMetadata if document type can be determined, None otherwise
        """
        path = Path(file_path)
        path_str = str(path).lower()
        filename = path.name.lower()
        
        # Determine document type based on directory structure
        if "/sensors/" in path_str or "\\sensors\\" in path_str:
            return self._tag_sensor_document(path_str, filename)
        elif "/algorithms/" in path_str or "\\algorithms\\" in path_str:
            return self._tag_algorithm_document(path_str, filename)
        elif "/regulations/" in path_str or "\\regulations\\" in path_str:
            return self._tag_regulation_document(path_str, filename)
        elif "/tests/" in path_str or "\\tests\\" in path_str:
            return self._tag_test_document(path_str, filename)
        else:
            logger.warning(f"Could not determine document type for: {file_path}")
            return None
    
    def _tag_sensor_document(self, path_str: str, filename: str) -> DocumentMetadata:
        """Tag a sensor document."""
        metadata = DocumentMetadata(document_type="sensor_doc")
        
        # Detect sensor type
        metadata.sensor_type = self._detect_pattern(
            path_str + " " + filename,
            self.SENSOR_PATTERNS
        )
        
        # Detect content type
        metadata.content_type = self._detect_pattern(
            filename,
            self.CONTENT_PATTERNS
        ) or "specification"  # Default to specification
        
        logger.debug(f"Tagged sensor document: type={metadata.sensor_type}, content={metadata.content_type}")
        return metadata
    
    def _tag_algorithm_document(self, path_str: str, filename: str) -> DocumentMetadata:
        """Tag an algorithm document."""
        metadata = DocumentMetadata(document_type="algorithm_doc")
        
        # Detect algorithm type
        metadata.algorithm_type = self._detect_pattern(
            path_str + " " + filename,
            self.ALGORITHM_PATTERNS
        )
        
        # Extract algorithm category from filename (e.g., "yolo_detection" -> "yolo")
        # This is a simple heuristic - can be enhanced
        if metadata.algorithm_type == "perception":
            if any(term in filename for term in ["yolo", "rcnn", "ssd"]):
                metadata.algorithm_category = "object_detection"
            elif any(term in filename for term in ["lane", "车道"]):
                metadata.algorithm_category = "lane_detection"
            elif any(term in filename for term in ["segment", "分割"]):
                metadata.algorithm_category = "segmentation"
        elif metadata.algorithm_type == "planning":
            if any(term in filename for term in ["path", "路径"]):
                metadata.algorithm_category = "path_planning"
            elif any(term in filename for term in ["trajectory", "轨迹"]):
                metadata.algorithm_category = "trajectory_planning"
        elif metadata.algorithm_type == "control":
            if any(term in filename for term in ["lateral", "横向"]):
                metadata.algorithm_category = "lateral_control"
            elif any(term in filename for term in ["longitudinal", "纵向"]):
                metadata.algorithm_category = "longitudinal_control"
        
        logger.debug(f"Tagged algorithm document: type={metadata.algorithm_type}, category={metadata.algorithm_category}")
        return metadata
    
    def _tag_regulation_document(self, path_str: str, filename: str) -> DocumentMetadata:
        """Tag a regulation document."""
        metadata = DocumentMetadata(document_type="regulation_doc")
        
        # Detect regulation type
        metadata.regulation_type = self._detect_pattern(
            path_str + " " + filename,
            self.REGULATION_PATTERNS
        ) or "industry_standard"  # Default
        
        # Extract standard number
        metadata.standard_number = self._extract_standard_number(filename)
        
        logger.debug(f"Tagged regulation document: type={metadata.regulation_type}, standard={metadata.standard_number}")
        return metadata
    
    def _tag_test_document(self, path_str: str, filename: str) -> DocumentMetadata:
        """Tag a test document."""
        metadata = DocumentMetadata(document_type="test_doc")
        
        # Detect test type
        metadata.test_type = self._detect_pattern(
            path_str + " " + filename,
            self.TEST_PATTERNS
        ) or "functional"  # Default to functional
        
        # Extract test category from filename
        if "acc" in filename or "跟车" in filename:
            metadata.test_category = "following"
        elif "lane" in filename or "变道" in filename:
            metadata.test_category = "lane_change"
        elif "overtake" in filename or "超车" in filename:
            metadata.test_category = "overtaking"
        elif "parking" in filename or "泊车" in filename:
            metadata.test_category = "parking"
        
        logger.debug(f"Tagged test document: type={metadata.test_type}, category={metadata.test_category}")
        return metadata
    
    def _detect_pattern(
        self,
        text: str,
        patterns: Dict[str, List[str]]
    ) -> Optional[str]:
        """Detect which pattern category matches the text.
        
        Args:
            text: Text to search in (lowercase)
            patterns: Dictionary of category -> list of regex patterns
        
        Returns:
            Matching category name or None
        """
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, text, re.IGNORECASE):
                    return category
        return None
    
    def _extract_standard_number(self, filename: str) -> Optional[str]:
        """Extract standard number from filename.
        
        Examples:
            "GB_T_40429-2021.pdf" -> "GB/T 40429-2021"
            "ISO_26262_part3.pdf" -> "ISO 26262"
        """
        # GB/T pattern - more flexible to handle various separators
        gb_match = re.search(r"gb[/_\s]*t?[/_\s]*(\d+(?:[-_]\d+)?)", filename, re.IGNORECASE)
        if gb_match:
            number = gb_match.group(1).replace("_", "-")
            return f"GB/T {number}"
        
        # ISO pattern
        iso_match = re.search(r"iso[/_\s]*(\d+)", filename, re.IGNORECASE)
        if iso_match:
            return f"ISO {iso_match.group(1)}"
        
        return None
    
    def tag_batch(self, file_paths: List[str]) -> Dict[str, Optional[DocumentMetadata]]:
        """Tag multiple documents in batch.
        
        Args:
            file_paths: List of file paths to tag
        
        Returns:
            Dictionary mapping file path to metadata
        """
        results = {}
        for file_path in file_paths:
            results[file_path] = self.tag_document(file_path)
        return results
    
    def get_metadata_summary(self, file_paths: List[str]) -> Dict[str, int]:
        """Get summary statistics of document types.
        
        Args:
            file_paths: List of file paths to analyze
        
        Returns:
            Dictionary with counts per document type
        """
        summary = {
            "sensor_doc": 0,
            "algorithm_doc": 0,
            "regulation_doc": 0,
            "test_doc": 0,
            "unknown": 0
        }
        
        for file_path in file_paths:
            metadata = self.tag_document(file_path)
            if metadata:
                summary[metadata.document_type] += 1
            else:
                summary["unknown"] += 1
        
        return summary


def create_metadata_tagger() -> ADMetadataTagger:
    """Factory function to create a metadata tagger instance.
    
    Returns:
        ADMetadataTagger instance
    """
    return ADMetadataTagger()
