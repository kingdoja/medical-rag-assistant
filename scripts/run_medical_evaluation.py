"""Run Medical Demo Evaluation.

Convenience script to run the 12-question medical demo evaluation
and generate a summary report.

Usage::

    python scripts/run_medical_evaluation.py
    python scripts/run_medical_evaluation.py --verbose
    python scripts/run_medical_evaluation.py --p0-only
    python scripts/run_medical_evaluation.py --p1-only
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.settings import load_settings
from src.core.query_engine.query_processor import QueryProcessor
from src.core.query_engine.hybrid_search import create_hybrid_search
from src.core.query_engine.dense_retriever import create_dense_retriever
from src.core.query_engine.sparse_retriever import create_sparse_retriever
from src.ingestion.storage.bm25_indexer import BM25Indexer
from src.libs.embedding.embedding_factory import EmbeddingFactory
from src.libs.vector_store.vector_store_factory import VectorStoreFactory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_test_set(test_set_path: Path) -> Dict[str, Any]:
    """Load medical demo test set."""
    with test_set_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def check_source_hit(results: List[Any], expected_sources: List[str]) -> bool:
    """Check if any expected source appears in results."""
    if not expected_sources:
        return True
    
    retrieved_sources = set()
    for result in results:
        if hasattr(result, 'metadata') and isinstance(result.metadata, dict):
            # Try both 'source' and 'source_path' keys
            source = result.metadata.get('source') or result.metadata.get('source_path', '')
        elif isinstance(result, dict):
            metadata = result.get('metadata', {})
            source = metadata.get('source') or metadata.get('source_path', '')
        else:
            continue
        
        if source:
            source_filename = Path(source).name
            retrieved_sources.add(source_filename)
    
    expected_set = set(expected_sources)
    return bool(expected_set & retrieved_sources)


def run_evaluation(
    test_set_path: Path,
    p0_only: bool = False,
    p1_only: bool = False,
    verbose: bool = False
) -> Dict[str, Any]:
    """Run medical demo evaluation.
    
    Args:
        test_set_path: Path to test set JSON
        p0_only: Only evaluate P0 priority scenarios
        p1_only: Only evaluate P1 priority scenarios
        verbose: Enable verbose logging
        
    Returns:
        Evaluation results summary
    """
    # Load test set
    test_data = load_test_set(test_set_path)
    test_cases = test_data["test_cases"]
    
    if p0_only:
        test_cases = [tc for tc in test_cases if tc.get("priority") == "P0"]
    elif p1_only:
        test_cases = [tc for tc in test_cases if tc.get("priority") == "P1"]
    
    logger.info(f"Loaded {len(test_cases)} test cases")
    
    # Initialize search engine with medical demo config
    try:
        # Load medical demo config directly
        import os
        medical_config_path = "config/settings.medical_demo.low_token.yaml"
        if not os.path.exists(medical_config_path):
            raise FileNotFoundError(f"Medical demo config not found: {medical_config_path}")
        
        logger.info(f"Using medical demo config: {medical_config_path}")
        settings = load_settings(path=medical_config_path)
        
        # Use medical_demo_v01 collection
        collection_name = "medical_demo_v01"
        logger.info(f"Using collection: {collection_name}")
        
        # Build components
        vector_store = VectorStoreFactory.create(
            settings,
            collection_name=collection_name,
        )
        
        embedding_client = EmbeddingFactory.create(settings)
        dense_retriever = create_dense_retriever(
            settings=settings,
            embedding_client=embedding_client,
            vector_store=vector_store,
        )
        
        bm25_indexer = BM25Indexer(index_dir=f"data/db/bm25/{collection_name}")
        sparse_retriever = create_sparse_retriever(
            settings=settings,
            bm25_indexer=bm25_indexer,
            vector_store=vector_store,
        )
        sparse_retriever.default_collection = collection_name
        
        query_processor = QueryProcessor()
        search = create_hybrid_search(
            settings=settings,
            query_processor=query_processor,
            dense_retriever=dense_retriever,
            sparse_retriever=sparse_retriever,
        )
        
        logger.info(f"Initialized HybridSearch successfully")
    except Exception as exc:
        logger.error(f"Failed to initialize search engine: {exc}")
        return {"error": str(exc)}
    
    # Run evaluation
    results = []
    hit_count = 0
    retrieval_case_count = 0
    
    for tc in test_cases:
        scenario_id = tc["scenario_id"]
        query = tc["query"]
        expected_sources = tc.get("expected_sources", [])
        validation_type = tc.get("validation_type")
        
        # Skip boundary scenarios for retrieval evaluation
        if validation_type in ["response_boundary", "response_content"]:
            if verbose:
                logger.info(f"Skipping {scenario_id} (boundary/content validation)")
            continue
        
        retrieval_case_count += 1
        
        try:
            # Run search
            search_results = search.search(query=query, top_k=10)
            
            # Check source hit
            hit = check_source_hit(search_results, expected_sources)
            
            if hit:
                hit_count += 1
            
            # Extract top sources
            top_sources = []
            for result in search_results[:3]:
                if hasattr(result, 'metadata') and isinstance(result.metadata, dict):
                    # Try both 'source' and 'source_path' keys
                    source = result.metadata.get('source') or result.metadata.get('source_path', '')
                elif isinstance(result, dict):
                    metadata = result.get('metadata', {})
                    source = metadata.get('source') or metadata.get('source_path', '')
                else:
                    continue
                
                if source:
                    top_sources.append(Path(source).name)
            
            result_entry = {
                "scenario_id": scenario_id,
                "query": query,
                "expected_sources": expected_sources,
                "top_sources": top_sources,
                "hit": hit,
                "num_results": len(search_results),
            }
            
            results.append(result_entry)
            
            if verbose or not hit:
                status = "✓" if hit else "✗"
                logger.info(f"{status} {scenario_id}: {query[:50]}...")
                logger.info(f"  Expected: {expected_sources}")
                logger.info(f"  Top 3: {top_sources}")
            
        except Exception as exc:
            logger.error(f"Search failed for {scenario_id}: {exc}")
            results.append({
                "scenario_id": scenario_id,
                "query": query,
                "error": str(exc),
                "hit": False,
            })
    
    # Calculate metrics
    hit_rate = hit_count / retrieval_case_count if retrieval_case_count > 0 else 0.0
    
    # Determine priority mode
    priority_mode = "P0" if p0_only else ("P1" if p1_only else "All")
    
    summary = {
        "total_cases": len(test_cases),
        "retrieval_cases": retrieval_case_count,
        "hit_count": hit_count,
        "hit_rate": hit_rate,
        "priority_mode": priority_mode,
        "results": results,
    }
    
    return summary


def print_summary(summary: Dict[str, Any]) -> None:
    """Print evaluation summary."""
    print("\n" + "=" * 60)
    print("Medical Demo Evaluation Summary")
    print("=" * 60)
    
    if "error" in summary:
        print(f"ERROR: {summary['error']}")
        return
    
    priority_mode = summary.get("priority_mode", "All")
    print(f"Priority Mode: {priority_mode}")
    print(f"Total Test Cases: {summary['total_cases']}")
    print(f"Retrieval Cases: {summary['retrieval_cases']}")
    print(f"Hit Count: {summary['hit_count']}")
    print(f"Hit Rate: {summary['hit_rate']:.2%}")
    print("=" * 60)
    
    # Print failed cases
    failed_cases = [r for r in summary['results'] if not r.get('hit', False)]
    if failed_cases:
        print(f"\nFailed Cases ({len(failed_cases)}):")
        for result in failed_cases:
            print(f"  [FAIL] {result['scenario_id']}: {result['query'][:50]}...")
            if 'error' in result:
                print(f"    Error: {result['error']}")
            else:
                print(f"    Expected: {result.get('expected_sources', [])}")
                print(f"    Got: {result.get('top_sources', [])}")
    
    # Print passed cases
    passed_cases = [r for r in summary['results'] if r.get('hit', False)]
    if passed_cases:
        print(f"\nPassed Cases ({len(passed_cases)}):")
        for result in passed_cases:
            print(f"  [PASS] {result['scenario_id']}: {result['query'][:50]}...")
    
    print("\n" + "=" * 60)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run medical demo evaluation")
    parser.add_argument(
        "--test-set",
        type=Path,
        default=Path("tests/fixtures/medical_demo_test_set.json"),
        help="Path to test set JSON file"
    )
    parser.add_argument(
        "--p0-only",
        action="store_true",
        help="Only evaluate P0 priority scenarios"
    )
    parser.add_argument(
        "--p1-only",
        action="store_true",
        help="Only evaluate P1 priority scenarios"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Save results to JSON file"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run evaluation
    summary = run_evaluation(
        test_set_path=args.test_set,
        p0_only=args.p0_only,
        p1_only=args.p1_only,
        verbose=args.verbose
    )
    
    # Print summary
    print_summary(summary)
    
    # Save results if requested
    if args.output:
        with args.output.open("w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        logger.info(f"Results saved to {args.output}")
    
    # Exit with error code if hit rate is too low
    if "error" not in summary:
        priority_mode = summary.get("priority_mode", "All")
        # Set threshold based on priority mode
        if priority_mode == "P0":
            min_hit_rate = 1.0  # 100% for P0
        elif priority_mode == "P1":
            min_hit_rate = 0.6  # 60% for P1
        else:
            min_hit_rate = 0.6  # 60% for all scenarios
        
        if summary['hit_rate'] < min_hit_rate:
            logger.error(f"Hit rate {summary['hit_rate']:.2%} below threshold {min_hit_rate:.2%}")
            sys.exit(1)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
