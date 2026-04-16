"""Unit tests for MetadataBooster component.

Tests cover:
- Query type detection (sensor, algorithm, regulation, test)
- Boost weight application
- Top-K verification
- Fallback mechanism
- Edge cases and error handling
"""

import pytest
from src.core.query_engine.metadata_booster import MetadataBooster, MetadataBoostResult
from src.core.types import RetrievalResult


class TestQueryTypeDetection:
    """Test query type detection functionality."""
    
    def test_detect_sensor_query_chinese(self):
        """Test sensor query detection with Chinese keywords."""
        booster = MetadataBooster()
        
        # Test various sensor queries
        assert booster.detect_query_type("激光雷达的探测距离是多少？") == "sensor_query"
        assert booster.detect_query_type("摄像头的分辨率和帧率") == "sensor_query"
        assert booster.detect_query_type("毫米波雷达的视场角") == "sensor_query"
        assert booster.detect_query_type("超声波传感器的标定方法") == "sensor_query"
    
    def test_detect_sensor_query_english(self):
        """Test sensor query detection with English keywords."""
        booster = MetadataBooster()
        
        assert booster.detect_query_type("What is the LiDAR detection range?") == "sensor_query"
        assert booster.detect_query_type("Camera resolution and frame rate") == "sensor_query"
        assert booster.detect_query_type("Radar calibration procedure") == "sensor_query"
    
    def test_detect_sensor_query_mixed(self):
        """Test sensor query detection with mixed Chinese-English."""
        booster = MetadataBooster()
        
        assert booster.detect_query_type("LiDAR 的探测距离") == "sensor_query"
        assert booster.detect_query_type("Camera 分辨率") == "sensor_query"
    
    def test_detect_algorithm_query_chinese(self):
        """Test algorithm query detection with Chinese keywords."""
        booster = MetadataBooster()
        
        assert booster.detect_query_type("感知算法的原理") == "algorithm_query"
        assert booster.detect_query_type("路径规划算法") == "algorithm_query"
        assert booster.detect_query_type("PID 控制算法") == "algorithm_query"
        assert booster.detect_query_type("目标检测算法") == "algorithm_query"
    
    def test_detect_algorithm_query_english(self):
        """Test algorithm query detection with English keywords."""
        booster = MetadataBooster()
        
        assert booster.detect_query_type("Perception algorithm principles") == "algorithm_query"
        assert booster.detect_query_type("Path planning algorithm") == "algorithm_query"
        assert booster.detect_query_type("SLAM algorithm") == "algorithm_query"
    
    def test_detect_regulation_query_chinese(self):
        """Test regulation query detection with Chinese keywords."""
        booster = MetadataBooster()
        
        assert booster.detect_query_type("GB/T 自动驾驶分级标准") == "regulation_query"
        assert booster.detect_query_type("ISO 26262 功能安全") == "regulation_query"
        assert booster.detect_query_type("测试规范要求") == "regulation_query"
    
    def test_detect_regulation_query_english(self):
        """Test regulation query detection with English keywords."""
        booster = MetadataBooster()
        
        assert booster.detect_query_type("ISO 26262 functional safety") == "regulation_query"
        assert booster.detect_query_type("ASIL level requirements") == "regulation_query"
    
    def test_detect_test_query_chinese(self):
        """Test test query detection with Chinese keywords."""
        booster = MetadataBooster()
        
        assert booster.detect_query_type("跟车场景测试用例") == "test_query"
        assert booster.detect_query_type("变道场景测试") == "test_query"
        assert booster.detect_query_type("紧急制动测试") == "test_query"
    
    def test_detect_test_query_english(self):
        """Test test query detection with English keywords."""
        booster = MetadataBooster()
        
        assert booster.detect_query_type("Lane change test scenario") == "test_query"
        assert booster.detect_query_type("Emergency braking test case") == "test_query"
    
    def test_detect_general_query(self):
        """Test general query detection (no specific type)."""
        booster = MetadataBooster()
        
        assert booster.detect_query_type("什么是自动驾驶？") == "general"
        assert booster.detect_query_type("Hello world") == "general"
        assert booster.detect_query_type("") == "general"
    
    def test_detect_query_type_priority(self):
        """Test query type detection when multiple patterns match."""
        booster = MetadataBooster()
        
        # Sensor + algorithm: should detect the one with more matches
        query = "激光雷达感知算法的探测距离"
        # This has both sensor (激光雷达, 探测距离) and algorithm (感知, 算法) keywords
        # Should detect based on match count
        result = booster.detect_query_type(query)
        assert result in ["sensor_query", "algorithm_query"]


class TestBoostApplication:
    """Test boost weight application functionality."""
    
    def create_mock_chunks(self, doc_types: list) -> list:
        """Create mock retrieval results with specified doc types."""
        chunks = []
        for i, doc_type in enumerate(doc_types):
            chunk = RetrievalResult(
                chunk_id=f"chunk_{i}",
                score=1.0 - (i * 0.1),  # Descending scores
                text=f"Content {i}",
                metadata={"doc_type": doc_type, "source_path": f"doc_{i}.pdf"}
            )
            chunks.append(chunk)
        return chunks
    
    def test_apply_boost_sensor_query(self):
        """Test boost application for sensor query."""
        booster = MetadataBooster()
        
        # Create chunks with mixed doc types
        chunks = self.create_mock_chunks([
            "algorithm_doc",  # score: 1.0
            "sensor_doc",     # score: 0.9
            "sensor_doc",     # score: 0.8
            "regulation_doc", # score: 0.7
        ])
        
        query = "激光雷达的探测距离"
        boosted = booster.apply_boost(chunks, query)
        
        # Sensor docs should be boosted (1.5x) and move to top
        assert boosted[0].metadata["doc_type"] == "sensor_doc"
        assert boosted[1].metadata["doc_type"] == "sensor_doc"
        
        # Check that scores were actually boosted
        # Original sensor_doc score: 0.9 * 1.5 = 1.35 > 1.0 (algorithm_doc)
        assert boosted[0].score > 1.0
    
    def test_apply_boost_algorithm_query(self):
        """Test boost application for algorithm query."""
        booster = MetadataBooster()
        
        chunks = self.create_mock_chunks([
            "sensor_doc",     # score: 1.0
            "algorithm_doc",  # score: 0.9
            "algorithm_doc",  # score: 0.8
            "test_doc",       # score: 0.7
        ])
        
        query = "感知算法的原理"
        boosted = booster.apply_boost(chunks, query)
        
        # Algorithm docs should be boosted and move to top
        assert boosted[0].metadata["doc_type"] == "algorithm_doc"
        assert boosted[1].metadata["doc_type"] == "algorithm_doc"
    
    def test_apply_boost_regulation_query(self):
        """Test boost application for regulation query."""
        booster = MetadataBooster()
        
        chunks = self.create_mock_chunks([
            "sensor_doc",      # score: 1.0
            "algorithm_doc",   # score: 0.9
            "regulation_doc",  # score: 0.8
            "test_doc",        # score: 0.7
        ])
        
        query = "ISO 26262 功能安全标准"
        boosted = booster.apply_boost(chunks, query)
        
        # Regulation doc should be boosted (1.6x) and move to top
        # 0.8 * 1.6 = 1.28 > 1.0
        assert boosted[0].metadata["doc_type"] == "regulation_doc"
    
    def test_apply_boost_general_query_no_change(self):
        """Test that general queries don't apply boost."""
        booster = MetadataBooster()
        
        chunks = self.create_mock_chunks([
            "sensor_doc",
            "algorithm_doc",
            "regulation_doc",
        ])
        
        query = "什么是自动驾驶？"
        boosted = booster.apply_boost(chunks, query)
        
        # Order should remain unchanged
        assert boosted[0].metadata["doc_type"] == "sensor_doc"
        assert boosted[1].metadata["doc_type"] == "algorithm_doc"
        assert boosted[2].metadata["doc_type"] == "regulation_doc"
    
    def test_apply_boost_empty_chunks(self):
        """Test boost application with empty chunks."""
        booster = MetadataBooster()
        
        chunks = []
        query = "激光雷达的探测距离"
        boosted = booster.apply_boost(chunks, query)
        
        assert boosted == []
    
    def test_apply_boost_preserves_metadata(self):
        """Test that boost preserves original metadata."""
        booster = MetadataBooster()
        
        chunks = [
            RetrievalResult(
                chunk_id="chunk_1",
                score=0.9,
                text="Content",
                metadata={
                    "doc_type": "sensor_doc",
                    "source_path": "doc.pdf",
                    "custom_field": "value"
                }
            )
        ]
        
        query = "激光雷达"
        boosted = booster.apply_boost(chunks, query)
        
        assert boosted[0].metadata["custom_field"] == "value"
        assert boosted[0].metadata["source_path"] == "doc.pdf"


class TestTopKVerification:
    """Test top-K verification functionality."""
    
    def create_mock_chunks(self, doc_types: list) -> list:
        """Create mock retrieval results with specified doc types."""
        chunks = []
        for i, doc_type in enumerate(doc_types):
            chunk = RetrievalResult(
                chunk_id=f"chunk_{i}",
                score=1.0 - (i * 0.1),
                text=f"Content {i}",
                metadata={"doc_type": doc_type, "source_path": f"doc_{i}.pdf"}
            )
            chunks.append(chunk)
        return chunks
    
    def test_top_k_verification_pass(self):
        """Test top-K verification passes when requirements met."""
        booster = MetadataBooster(top_k_threshold=3, top_k_min_count=2)
        
        # Top-3 has 2 sensor_doc
        chunks = self.create_mock_chunks([
            "sensor_doc",
            "sensor_doc",
            "algorithm_doc",
            "regulation_doc",
        ])
        
        query = "激光雷达的探测距离"
        result = booster.apply_boost_with_details(chunks, query)
        
        assert result.top_k_verified is True
        assert result.fallback_used is False
    
    def test_top_k_verification_fail(self):
        """Test top-K verification fails when requirements not met."""
        booster = MetadataBooster(top_k_threshold=3, top_k_min_count=2)
        
        # Create scenario where even with boost, top-3 won't have 2 sensor_docs
        # Algorithm docs have very high scores that even boosted sensor docs can't beat
        chunks = [
            RetrievalResult(
                chunk_id="chunk_0",
                score=1.0,
                text="Content 0",
                metadata={"doc_type": "algorithm_doc", "source_path": "doc_0.pdf"}
            ),
            RetrievalResult(
                chunk_id="chunk_1",
                score=0.95,
                text="Content 1",
                metadata={"doc_type": "algorithm_doc", "source_path": "doc_1.pdf"}
            ),
            RetrievalResult(
                chunk_id="chunk_2",
                score=0.90,
                text="Content 2",
                metadata={"doc_type": "regulation_doc", "source_path": "doc_2.pdf"}
            ),
            RetrievalResult(
                chunk_id="chunk_3",
                score=0.50,  # Low score, even with 1.5x boost = 0.75, won't reach top-3
                text="Content 3",
                metadata={"doc_type": "sensor_doc", "source_path": "doc_3.pdf"}
            ),
            RetrievalResult(
                chunk_id="chunk_4",
                score=0.45,  # Low score, even with 1.5x boost = 0.675, won't reach top-3
                text="Content 4",
                metadata={"doc_type": "sensor_doc", "source_path": "doc_4.pdf"}
            ),
        ]
        
        query = "激光雷达的探测距离"
        result = booster.apply_boost_with_details(chunks, query)
        
        # Verification should fail, fallback should be used
        assert result.top_k_verified is False
        assert result.fallback_used is True
        assert result.boosted_chunks == chunks  # Original chunks returned
    
    def test_top_k_verification_insufficient_chunks(self):
        """Test top-K verification with fewer chunks than threshold."""
        booster = MetadataBooster(top_k_threshold=3, top_k_min_count=2)
        
        # Only 2 chunks (less than threshold of 3)
        chunks = self.create_mock_chunks([
            "sensor_doc",
            "algorithm_doc",
        ])
        
        query = "激光雷达的探测距离"
        result = booster.apply_boost_with_details(chunks, query)
        
        # Should pass verification (not enough chunks to verify)
        assert result.top_k_verified is True


class TestFallbackMechanism:
    """Test fallback mechanism functionality."""
    
    def create_mock_chunks(self, doc_types: list) -> list:
        """Create mock retrieval results with specified doc types."""
        chunks = []
        for i, doc_type in enumerate(doc_types):
            chunk = RetrievalResult(
                chunk_id=f"chunk_{i}",
                score=1.0 - (i * 0.1),
                text=f"Content {i}",
                metadata={"doc_type": doc_type, "source_path": f"doc_{i}.pdf"}
            )
            chunks.append(chunk)
        return chunks
    
    def test_fallback_when_verification_fails(self):
        """Test fallback to original results when verification fails."""
        booster = MetadataBooster(top_k_threshold=3, top_k_min_count=2)
        
        # Create scenario where boost won't help
        chunks = self.create_mock_chunks([
            "algorithm_doc",  # score: 1.0
            "algorithm_doc",  # score: 0.9
            "algorithm_doc",  # score: 0.8
            "sensor_doc",     # score: 0.7
        ])
        
        query = "激光雷达的探测距离"  # Sensor query
        result = booster.apply_boost_with_details(chunks, query)
        
        # Should use fallback (original results)
        assert result.fallback_used is True
        assert result.boosted_chunks == chunks
    
    def test_no_fallback_when_verification_passes(self):
        """Test no fallback when verification passes."""
        booster = MetadataBooster(top_k_threshold=3, top_k_min_count=2)
        
        chunks = self.create_mock_chunks([
            "algorithm_doc",
            "sensor_doc",
            "sensor_doc",
            "regulation_doc",
        ])
        
        query = "激光雷达的探测距离"
        result = booster.apply_boost_with_details(chunks, query)
        
        assert result.fallback_used is False
        assert result.boosted_chunks != chunks  # Boosted results returned


class TestBoostConfiguration:
    """Test boost configuration functionality."""
    
    def test_custom_boost_config(self):
        """Test custom boost configuration."""
        custom_config = {
            "sensor_query": {
                "sensor_doc": 2.0,  # Higher boost
                "algorithm_doc": 0.5,
            }
        }
        
        booster = MetadataBooster(boost_config=custom_config)
        
        chunks = [
            RetrievalResult(
                chunk_id="chunk_1",
                score=0.8,
                text="Content",
                metadata={"doc_type": "sensor_doc", "source_path": "doc.pdf"}
            )
        ]
        
        query = "激光雷达"
        boosted = booster.apply_boost(chunks, query)
        
        # Score should be boosted by 2.0x
        assert boosted[0].score == 0.8 * 2.0
    
    def test_default_boost_config(self):
        """Test default boost configuration is applied."""
        booster = MetadataBooster()
        
        # Check default config exists
        assert "sensor_query" in booster.boost_config
        assert "algorithm_query" in booster.boost_config
        assert "regulation_query" in booster.boost_config
        assert "test_query" in booster.boost_config
        
        # Check default weights
        assert booster.boost_config["sensor_query"]["sensor_doc"] == 1.5
        assert booster.boost_config["algorithm_query"]["algorithm_doc"] == 1.3
        assert booster.boost_config["regulation_query"]["regulation_doc"] == 1.6
    
    def test_missing_doc_type_uses_default_weight(self):
        """Test that missing doc types use default weight of 1.0."""
        booster = MetadataBooster()
        
        chunks = [
            RetrievalResult(
                chunk_id="chunk_1",
                score=0.9,
                text="Content",
                metadata={"doc_type": "unknown_type", "source_path": "doc.pdf"}
            )
        ]
        
        query = "激光雷达"
        boosted = booster.apply_boost(chunks, query)
        
        # Score should remain unchanged (weight = 1.0)
        assert boosted[0].score == 0.9


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_query(self):
        """Test handling of empty query."""
        booster = MetadataBooster()
        
        assert booster.detect_query_type("") == "general"
        assert booster.detect_query_type(None) == "general"
    
    def test_chunks_without_doc_type(self):
        """Test handling of chunks without doc_type metadata."""
        booster = MetadataBooster()
        
        chunks = [
            RetrievalResult(
                chunk_id="chunk_1",
                score=0.9,
                text="Content",
                metadata={"source_path": "doc.pdf"}  # No doc_type
            )
        ]
        
        query = "激光雷达"
        boosted = booster.apply_boost(chunks, query)
        
        # Should handle gracefully (use default weight 1.0)
        assert len(boosted) == 1
        assert boosted[0].score == 0.9
    
    def test_apply_boost_with_details_returns_complete_result(self):
        """Test that apply_boost_with_details returns complete result."""
        booster = MetadataBooster()
        
        chunks = [
            RetrievalResult(
                chunk_id="chunk_1",
                score=0.9,
                text="Content",
                metadata={"doc_type": "sensor_doc", "source_path": "doc.pdf"}
            )
        ]
        
        query = "激光雷达"
        result = booster.apply_boost_with_details(chunks, query)
        
        assert isinstance(result, MetadataBoostResult)
        assert result.original_chunks == chunks
        assert len(result.boosted_chunks) > 0
        assert result.boost_type == "sensor_query"
        assert len(result.boost_config) > 0
