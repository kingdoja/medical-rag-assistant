"""Simple Medical Demo Evaluation Runner.

This script runs evaluation using the medical demo configuration directly.

Usage::

    python scripts/run_medical_eval_simple.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Set medical demo config before importing anything else
os.environ["SETTINGS_PATH"] = "config/settings.medical_demo.low_token.yaml"

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.settings import load_settings
from src.core.query_engine.hybrid_search import HybridSearch

def main():
    print("=" * 60)
    print("Medical Demo Evaluation - Simple Runner")
    print("=" * 60)
    
    # Load test set
    test_set_path = Path("tests/fixtures/medical_demo_test_set.json")
    if not test_set_path.exists():
        print(f"ERROR: Test set not found: {test_set_path}")
        return
    
    with test_set_path.open("r", encoding="utf-8") as f:
        test_data = json.load(f)
    
    test_cases = test_data["test_cases"]
    p0_cases = [tc for tc in test_cases if tc.get("priority") == "P0"]
    
    print(f"Loaded {len(test_cases)} test cases ({len(p0_cases)} P0)")
    print()
    
    # Load settings
    print("Loading medical demo configuration...")
    try:
        settings = load_settings()
        print(f"✓ Settings loaded")
        print(f"  Collection: {settings.vector_store.collection_name}")
        print(f"  Embedding: {settings.embedding.provider}")
        print()
    except Exception as exc:
        print(f"✗ Failed to load settings: {exc}")
        return
    
    # Initialize search
    print("Initializing HybridSearch...")
    try:
        search = HybridSearch(settings)
        print(f"✓ HybridSearch initialized")
        print()
    except Exception as exc:
        print(f"✗ Failed to initialize search: {exc}")
        return
    
    # Run evaluation on P0 cases only
    print("Running evaluation on P0 scenarios...")
    print("-" * 60)
    
    hit_count = 0
    retrieval_count = 0
    
    for tc in p0_cases:
        scenario_id = tc["scenario_id"]
        query = tc["query"]
        expected_sources = tc.get("expected_sources", [])
        validation_type = tc.get("validation_type")
        
        # Skip boundary scenarios
        if validation_type in ["response_boundary", "response_content"]:
            print(f"⏭️  {scenario_id}: Skipped (boundary validation)")
            continue
        
        retrieval_count += 1
        
        try:
            # Run search
            results = search.search(query=query, top_k=10)
            
            # Check source hit
            retrieved_sources = set()
            for result in results[:10]:
                if hasattr(result, 'metadata') and isinstance(result.metadata, dict):
                    source = result.metadata.get('source', '')
                elif isinstance(result, dict):
                    source = result.get('metadata', {}).get('source', '')
                else:
                    continue
                
                if source:
                    source_filename = Path(source).name
                    retrieved_sources.add(source_filename)
            
            expected_set = set(expected_sources)
            hit = bool(expected_set & retrieved_sources)
            
            if hit:
                hit_count += 1
                print(f"✅ {scenario_id}: PASS")
                print(f"   Expected: {expected_sources}")
                print(f"   Hit: {expected_set & retrieved_sources}")
            else:
                print(f"❌ {scenario_id}: FAIL")
                print(f"   Expected: {expected_sources}")
                print(f"   Got: {list(retrieved_sources)[:3]}")
            
        except Exception as exc:
            print(f"⚠️  {scenario_id}: ERROR - {exc}")
        
        print()
    
    # Summary
    print("=" * 60)
    print("Evaluation Summary")
    print("=" * 60)
    print(f"Total P0 Scenarios: {len(p0_cases)}")
    print(f"Retrieval Scenarios: {retrieval_count}")
    print(f"Passed: {hit_count}")
    print(f"Failed: {retrieval_count - hit_count}")
    
    if retrieval_count > 0:
        hit_rate = hit_count / retrieval_count
        print(f"Hit Rate: {hit_rate:.2%}")
        
        if hit_rate >= 0.6:
            print("✅ Demo Ready! (>= 60% threshold)")
        else:
            print("❌ Demo Not Ready (< 60% threshold)")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
