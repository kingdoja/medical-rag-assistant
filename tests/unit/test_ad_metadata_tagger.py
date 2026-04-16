"""Unit tests for ADMetadataTagger."""

import pytest
from src.ingestion.metadata.ad_metadata_tagger import (
    ADMetadataTagger,
    DocumentMetadata,
    create_metadata_tagger,
)


class TestADMetadataTagger:
    """Test suite for ADMetadataTagger."""
    
    def test_factory_function(self):
        """Test factory function creates tagger instance."""
        tagger = create_metadata_tagger()
        assert isinstance(tagger, ADMetadataTagger)
    
    # ─────────────────────────────────────────────────────────────
    # Sensor Document Tests
    # ─────────────────────────────────────────────────────────────
    
    def test_tag_camera_sensor_document(self):
        """Test tagging camera sensor document."""
        tagger = ADMetadataTagger()
        
        metadata = tagger.tag_document("demo-data-ad/sensors/camera/spec.pdf")
        
        assert metadata is not None
        assert metadata.document_type == "sensor_doc"
        assert metadata.sensor_type == "camera"
        assert metadata.content_type == "specification"
    
    def test_tag_lidar_sensor_document(self):
        """Test tagging LiDAR sensor document."""
        tagger = ADMetadataTagger()
        
        metadata = tagger.tag_document("demo-data-ad/sensors/lidar/velodyne_vls128_spec.pdf")
        
        assert metadata is not None
        assert metadata.document_type == "sensor_doc"
        assert metadata.sensor_type == "lidar"
        assert metadata.content_type == "specification"
    
    def test_tag_radar_sensor_document(self):
        """Test tagging radar sensor document."""
        tagger = ADMetadataTagger()
        
        metadata = tagger.tag_document("demo-data-ad/sensors/radar/continental_ars540_datasheet.pdf")
        
        assert metadata is not None
        assert metadata.document_type == "sensor_doc"
        assert metadata.sensor_type == "radar"
    
    def test_tag_ultrasonic_sensor_document(self):
        """Test tagging ultrasonic sensor document."""
        tagger = ADMetadataTagger()
        
        metadata = tagger.tag_document("demo-data-ad/sensors/ultrasonic/bosch_uss_spec.pdf")
        
        assert metadata is not None
        assert metadata.document_type == "sensor_doc"
        assert metadata.sensor_type == "ultrasonic"
    
    def test_tag_sensor_calibration_document(self):
        """Test tagging sensor calibration document."""
        tagger = ADMetadataTagger()
        
        metadata = tagger.tag_document("demo-data-ad/sensors/camera/camera_calibration_guide.pdf")
        
        assert metadata is not None
        assert metadata.document_type == "sensor_doc"
        assert metadata.sensor_type == "camera"
        assert metadata.content_type == "calibration"
    
    def test_tag_sensor_chinese_filename(self):
        """Test tagging sensor document with Chinese filename."""
        tagger = ADMetadataTagger()
        
        metadata = tagger.tag_document("demo-data-ad/sensors/camera/摄像头规格书.pdf")
        
        assert metadata is not None
        assert metadata.document_type == "sensor_doc"
        assert metadata.sensor_type == "camera"
    
    # ─────────────────────────────────────────────────────────────
    # Algorithm Document Tests
    # ─────────────────────────────────────────────────────────────
    
    def test_tag_perception_algorithm_document(self):
        """Test tagging perception algorithm document."""
        tagger = ADMetadataTagger()
        
        metadata = tagger.tag_document("demo-data-ad/algorithms/perception/yolo_object_detection.pdf")
        
        assert metadata is not None
        assert metadata.document_type == "algorithm_doc"
        assert metadata.algorithm_type == "perception"
        assert metadata.algorithm_category == "object_detection"
    
    def test_tag_planning_algorithm_document(self):
        """Test tagging planning algorithm document."""
        tagger = ADMetadataTagger()
        
        metadata = tagger.tag_document("demo-data-ad/algorithms/planning/path_planning_algorithm.pdf")
        
        assert metadata is not None
        assert metadata.document_type == "algorithm_doc"
        assert metadata.algorithm_type == "planning"
        assert metadata.algorithm_category == "path_planning"
    
    def test_tag_control_algorithm_document(self):
        """Test tagging control algorithm document."""
        tagger = ADMetadataTagger()
        
        metadata = tagger.tag_document("demo-data-ad/algorithms/control/mpc_lateral_control.pdf")
        
        assert metadata is not None
        assert metadata.document_type == "algorithm_doc"
        assert metadata.algorithm_type == "control"
        assert metadata.algorithm_category == "lateral_control"
    
    def test_tag_slam_algorithm_document(self):
        """Test tagging SLAM algorithm document."""
        tagger = ADMetadataTagger()
        
        metadata = tagger.tag_document("demo-data-ad/algorithms/slam/visual_slam_algorithm.pdf")
        
        assert metadata is not None
        assert metadata.document_type == "algorithm_doc"
        assert metadata.algorithm_type == "slam"
    
    def test_tag_algorithm_chinese_filename(self):
        """Test tagging algorithm document with Chinese filename."""
        tagger = ADMetadataTagger()
        
        metadata = tagger.tag_document("demo-data-ad/algorithms/perception/目标检测算法.pdf")
        
        assert metadata is not None
        assert metadata.document_type == "algorithm_doc"
        assert metadata.algorithm_type == "perception"
    
    # ─────────────────────────────────────────────────────────────
    # Regulation Document Tests
    # ─────────────────────────────────────────────────────────────
    
    def test_tag_national_standard_document(self):
        """Test tagging national standard document."""
        tagger = ADMetadataTagger()
        
        metadata = tagger.tag_document("demo-data-ad/regulations/national/GB_T_40429-2021.pdf")
        
        assert metadata is not None
        assert metadata.document_type == "regulation_doc"
        assert metadata.regulation_type == "national_standard"
        assert metadata.standard_number == "GB/T 40429-2021"
    
    def test_tag_iso_standard_document(self):
        """Test tagging ISO standard document."""
        tagger = ADMetadataTagger()
        
        metadata = tagger.tag_document("demo-data-ad/regulations/iso/ISO_26262_part3.pdf")
        
        assert metadata is not None
        assert metadata.document_type == "regulation_doc"
        assert metadata.regulation_type == "iso_standard"
        assert metadata.standard_number == "ISO 26262"
    
    def test_tag_test_spec_document(self):
        """Test tagging test specification document."""
        tagger = ADMetadataTagger()
        
        metadata = tagger.tag_document("demo-data-ad/regulations/test_spec/functional_test_standard.pdf")
        
        assert metadata is not None
        assert metadata.document_type == "regulation_doc"
        assert metadata.regulation_type == "test_spec"
    
    def test_tag_regulation_chinese_filename(self):
        """Test tagging regulation document with Chinese filename."""
        tagger = ADMetadataTagger()
        
        metadata = tagger.tag_document("demo-data-ad/regulations/national/国标_自动驾驶分级.pdf")
        
        assert metadata is not None
        assert metadata.document_type == "regulation_doc"
        assert metadata.regulation_type == "national_standard"
    
    # ─────────────────────────────────────────────────────────────
    # Test Document Tests
    # ─────────────────────────────────────────────────────────────
    
    def test_tag_functional_test_document(self):
        """Test tagging functional test document."""
        tagger = ADMetadataTagger()
        
        metadata = tagger.tag_document("demo-data-ad/tests/functional/acc_following_test.pdf")
        
        assert metadata is not None
        assert metadata.document_type == "test_doc"
        assert metadata.test_type == "functional"
        assert metadata.test_category == "following"
    
    def test_tag_safety_test_document(self):
        """Test tagging safety test document."""
        tagger = ADMetadataTagger()
        
        metadata = tagger.tag_document("demo-data-ad/tests/safety/collision_avoidance_test.pdf")
        
        assert metadata is not None
        assert metadata.document_type == "test_doc"
        assert metadata.test_type == "safety"
    
    def test_tag_boundary_test_document(self):
        """Test tagging boundary test document."""
        tagger = ADMetadataTagger()
        
        metadata = tagger.tag_document("demo-data-ad/tests/boundary/extreme_weather_test.pdf")
        
        assert metadata is not None
        assert metadata.document_type == "test_doc"
        assert metadata.test_type == "boundary"
    
    def test_tag_simulation_test_document(self):
        """Test tagging simulation test document."""
        tagger = ADMetadataTagger()
        
        metadata = tagger.tag_document("demo-data-ad/tests/simulation/carla_simulation_test.pdf")
        
        assert metadata is not None
        assert metadata.document_type == "test_doc"
        assert metadata.test_type == "simulation"
    
    def test_tag_test_chinese_filename(self):
        """Test tagging test document with Chinese filename."""
        tagger = ADMetadataTagger()
        
        metadata = tagger.tag_document("demo-data-ad/tests/functional/功能测试_跟车场景.pdf")
        
        assert metadata is not None
        assert metadata.document_type == "test_doc"
        assert metadata.test_type == "functional"
    
    # ─────────────────────────────────────────────────────────────
    # Edge Cases and Error Handling
    # ─────────────────────────────────────────────────────────────
    
    def test_tag_unknown_document_type(self):
        """Test tagging document with unknown type."""
        tagger = ADMetadataTagger()
        
        metadata = tagger.tag_document("demo-data-ad/unknown/random_document.pdf")
        
        assert metadata is None
    
    def test_tag_document_windows_path(self):
        """Test tagging document with Windows path."""
        tagger = ADMetadataTagger()
        
        metadata = tagger.tag_document("demo-data-ad\\sensors\\camera\\spec.pdf")
        
        assert metadata is not None
        assert metadata.document_type == "sensor_doc"
        assert metadata.sensor_type == "camera"
    
    def test_metadata_to_dict(self):
        """Test DocumentMetadata to_dict method."""
        metadata = DocumentMetadata(
            document_type="sensor_doc",
            sensor_type="camera",
            content_type="specification"
        )
        
        result = metadata.to_dict()
        
        assert result["document_type"] == "sensor_doc"
        assert result["sensor_type"] == "camera"
        assert result["content_type"] == "specification"
        assert "algorithm_type" not in result  # None values excluded
    
    def test_metadata_to_dict_excludes_none(self):
        """Test that to_dict excludes None values."""
        metadata = DocumentMetadata(
            document_type="algorithm_doc",
            algorithm_type="perception"
        )
        
        result = metadata.to_dict()
        
        assert "sensor_type" not in result
        assert "regulation_type" not in result
        assert "test_type" not in result
    
    # ─────────────────────────────────────────────────────────────
    # Batch Operations
    # ─────────────────────────────────────────────────────────────
    
    def test_tag_batch(self):
        """Test batch tagging of multiple documents."""
        tagger = ADMetadataTagger()
        
        file_paths = [
            "demo-data-ad/sensors/camera/spec.pdf",
            "demo-data-ad/algorithms/perception/yolo.pdf",
            "demo-data-ad/regulations/national/GB_T_40429.pdf",
            "demo-data-ad/tests/functional/acc_test.pdf"
        ]
        
        results = tagger.tag_batch(file_paths)
        
        assert len(results) == 4
        assert results[file_paths[0]].document_type == "sensor_doc"
        assert results[file_paths[1]].document_type == "algorithm_doc"
        assert results[file_paths[2]].document_type == "regulation_doc"
        assert results[file_paths[3]].document_type == "test_doc"
    
    def test_get_metadata_summary(self):
        """Test getting metadata summary statistics."""
        tagger = ADMetadataTagger()
        
        file_paths = [
            "demo-data-ad/sensors/camera/spec1.pdf",
            "demo-data-ad/sensors/lidar/spec2.pdf",
            "demo-data-ad/algorithms/perception/algo1.pdf",
            "demo-data-ad/algorithms/planning/algo2.pdf",
            "demo-data-ad/algorithms/control/algo3.pdf",
            "demo-data-ad/regulations/national/reg1.pdf",
            "demo-data-ad/tests/functional/test1.pdf",
            "demo-data-ad/tests/safety/test2.pdf",
            "demo-data-ad/unknown/unknown.pdf"
        ]
        
        summary = tagger.get_metadata_summary(file_paths)
        
        assert summary["sensor_doc"] == 2
        assert summary["algorithm_doc"] == 3
        assert summary["regulation_doc"] == 1
        assert summary["test_doc"] == 2
        assert summary["unknown"] == 1
    
    # ─────────────────────────────────────────────────────────────
    # Pattern Detection Tests
    # ─────────────────────────────────────────────────────────────
    
    def test_detect_sensor_type_from_manufacturer(self):
        """Test detecting sensor type from manufacturer name."""
        tagger = ADMetadataTagger()
        
        # Velodyne is a LiDAR manufacturer
        metadata = tagger.tag_document("demo-data-ad/sensors/velodyne_vls128.pdf")
        assert metadata.sensor_type == "lidar"
        
        # Continental makes radars
        metadata = tagger.tag_document("demo-data-ad/sensors/continental_ars540.pdf")
        assert metadata.sensor_type == "radar"
    
    def test_extract_standard_number_variations(self):
        """Test extracting standard numbers with various formats."""
        tagger = ADMetadataTagger()
        
        # GB/T with underscore
        metadata = tagger.tag_document("demo-data-ad/regulations/GB_T_40429-2021.pdf")
        assert metadata.standard_number == "GB/T 40429-2021"
        
        # GB/T with slash in filename (not directory)
        metadata = tagger.tag_document("demo-data-ad/regulations/GBT_34590.pdf")
        assert metadata.standard_number == "GB/T 34590"
        
        # ISO
        metadata = tagger.tag_document("demo-data-ad/regulations/ISO_26262.pdf")
        assert metadata.standard_number == "ISO 26262"
    
    def test_algorithm_category_detection(self):
        """Test algorithm category detection from filename."""
        tagger = ADMetadataTagger()
        
        # Lane detection
        metadata = tagger.tag_document("demo-data-ad/algorithms/perception/lane_detection.pdf")
        assert metadata.algorithm_category == "lane_detection"
        
        # Trajectory planning
        metadata = tagger.tag_document("demo-data-ad/algorithms/planning/trajectory_planning.pdf")
        assert metadata.algorithm_category == "trajectory_planning"
        
        # Longitudinal control
        metadata = tagger.tag_document("demo-data-ad/algorithms/control/longitudinal_control.pdf")
        assert metadata.algorithm_category == "longitudinal_control"
    
    def test_test_category_detection(self):
        """Test test category detection from filename."""
        tagger = ADMetadataTagger()
        
        # Lane change
        metadata = tagger.tag_document("demo-data-ad/tests/functional/lane_change_test.pdf")
        assert metadata.test_category == "lane_change"
        
        # Overtaking
        metadata = tagger.tag_document("demo-data-ad/tests/functional/overtake_scenario.pdf")
        assert metadata.test_category == "overtaking"
        
        # Parking
        metadata = tagger.tag_document("demo-data-ad/tests/functional/parking_test.pdf")
        assert metadata.test_category == "parking"
