"""Unit tests for P1 evaluation support in medical demo evaluation."""
from __future__ import annotations

import json
from pathlib import Path


def test_p1_filtering():
    """Test that P1 scenarios can be filtered correctly."""
    test_set_path = Path("tests/fixtures/medical_demo_test_set.json")
    
    with test_set_path.open("r", encoding="utf-8") as f:
        test_data = json.load(f)
    
    test_cases = test_data["test_cases"]
    
    # Filter P1 scenarios
    p1_cases = [tc for tc in test_cases if tc.get("priority") == "P1"]
    
    # Verify P1 scenarios exist
    assert len(p1_cases) == 4, f"Expected 4 P1 scenarios, got {len(p1_cases)}"
    
    # Verify all are P1
    assert all(tc.get("priority") == "P1" for tc in p1_cases)
    
    # Verify expected P1 scenario IDs
    p1_ids = {tc["scenario_id"] for tc in p1_cases}
    expected_p1_ids = {"S8", "S9", "S10", "S11"}
    assert p1_ids == expected_p1_ids, f"Expected {expected_p1_ids}, got {p1_ids}"


def test_p0_filtering():
    """Test that P0 scenarios can be filtered correctly."""
    test_set_path = Path("tests/fixtures/medical_demo_test_set.json")
    
    with test_set_path.open("r", encoding="utf-8") as f:
        test_data = json.load(f)
    
    test_cases = test_data["test_cases"]
    
    # Filter P0 scenarios
    p0_cases = [tc for tc in test_cases if tc.get("priority") == "P0"]
    
    # Verify P0 scenarios exist
    assert len(p0_cases) == 8, f"Expected 8 P0 scenarios, got {len(p0_cases)}"
    
    # Verify all are P0
    assert all(tc.get("priority") == "P0" for tc in p0_cases)


def test_priority_mode_determination():
    """Test priority mode determination logic."""
    # Test P0 mode
    p0_only = True
    p1_only = False
    priority_mode = "P0" if p0_only else ("P1" if p1_only else "All")
    assert priority_mode == "P0"
    
    # Test P1 mode
    p0_only = False
    p1_only = True
    priority_mode = "P0" if p0_only else ("P1" if p1_only else "All")
    assert priority_mode == "P1"
    
    # Test All mode
    p0_only = False
    p1_only = False
    priority_mode = "P0" if p0_only else ("P1" if p1_only else "All")
    assert priority_mode == "All"


def test_threshold_selection():
    """Test that correct thresholds are selected based on priority mode."""
    MIN_HIT_RATE_P0 = 1.0
    MIN_HIT_RATE_P1 = 0.6
    
    # P0 mode should use 100% threshold
    priority_mode = "P0"
    threshold = MIN_HIT_RATE_P0 if priority_mode == "P0" else MIN_HIT_RATE_P1
    assert threshold == 1.0
    
    # P1 mode should use 60% threshold
    priority_mode = "P1"
    threshold = MIN_HIT_RATE_P0 if priority_mode == "P0" else MIN_HIT_RATE_P1
    assert threshold == 0.6
    
    # All mode should use 60% threshold
    priority_mode = "All"
    threshold = MIN_HIT_RATE_P0 if priority_mode == "P0" else MIN_HIT_RATE_P1
    assert threshold == 0.6


def test_readiness_calculation():
    """Test P0 and P1 readiness calculation logic."""
    MIN_HIT_RATE_P0 = 1.0
    MIN_HIT_RATE_P1 = 0.6
    
    # Test P0 ready, P1 ready
    p0_hit_rate = 1.0
    p1_hit_rate = 0.8
    p0_retrieval = [1, 2, 3]  # Non-empty
    p1_retrieval = [1, 2, 3]  # Non-empty
    
    p0_ready = p0_hit_rate >= MIN_HIT_RATE_P0 if p0_retrieval else True
    p1_ready = p1_hit_rate >= MIN_HIT_RATE_P1 if p1_retrieval else True
    demo_ready = p0_ready and (p1_ready if p1_retrieval else True)
    
    assert p0_ready is True
    assert p1_ready is True
    assert demo_ready is True
    
    # Test P0 ready, P1 not ready
    p0_hit_rate = 1.0
    p1_hit_rate = 0.5  # Below threshold
    
    p0_ready = p0_hit_rate >= MIN_HIT_RATE_P0 if p0_retrieval else True
    p1_ready = p1_hit_rate >= MIN_HIT_RATE_P1 if p1_retrieval else True
    demo_ready = p0_ready and (p1_ready if p1_retrieval else True)
    
    assert p0_ready is True
    assert p1_ready is False
    assert demo_ready is False
    
    # Test P0 not ready, P1 ready
    p0_hit_rate = 0.8  # Below threshold
    p1_hit_rate = 0.8
    
    p0_ready = p0_hit_rate >= MIN_HIT_RATE_P0 if p0_retrieval else True
    p1_ready = p1_hit_rate >= MIN_HIT_RATE_P1 if p1_retrieval else True
    demo_ready = p0_ready and (p1_ready if p1_retrieval else True)
    
    assert p0_ready is False
    assert p1_ready is True
    assert demo_ready is False
    
    # Test no P1 scenarios (P1 should default to ready)
    p0_hit_rate = 1.0
    p1_retrieval = []  # Empty
    
    p0_ready = p0_hit_rate >= MIN_HIT_RATE_P0 if p0_retrieval else True
    p1_ready = p1_hit_rate >= MIN_HIT_RATE_P1 if p1_retrieval else True
    demo_ready = p0_ready and (p1_ready if p1_retrieval else True)
    
    assert p0_ready is True
    assert p1_ready is True  # Defaults to True when no P1 scenarios
    assert demo_ready is True
