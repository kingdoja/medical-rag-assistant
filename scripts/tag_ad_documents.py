#!/usr/bin/env python
"""CLI tool for tagging autonomous driving documents with metadata.

This script analyzes documents in the demo-data-ad directory and generates
metadata tags based on their location and filename patterns.

Usage:
    # Analyze all documents and show summary
    python scripts/tag_ad_documents.py --path demo-data-ad --summary
    
    # Analyze specific document
    python scripts/tag_ad_documents.py --path demo-data-ad/sensors/camera/spec.pdf
    
    # Generate metadata JSON files for all documents
    python scripts/tag_ad_documents.py --path demo-data-ad --generate-json
    
    # Validate existing metadata
    python scripts/tag_ad_documents.py --path demo-data-ad --validate
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Ensure project root is on sys.path
_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent
sys.path.insert(0, str(_REPO_ROOT))

from src.ingestion.metadata.ad_metadata_tagger import ADMetadataTagger, DocumentMetadata


def discover_documents(path: Path, extensions: List[str] = None) -> List[Path]:
    """Discover documents to tag.
    
    Args:
        path: File or directory path
        extensions: List of file extensions to include (default: ['.pdf'])
    
    Returns:
        List of document paths
    """
    if extensions is None:
        extensions = ['.pdf', '.md', '.txt']
    
    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")
    
    if path.is_file():
        return [path]
    
    # Directory: recursively find all matching files
    files = []
    for ext in extensions:
        files.extend(path.rglob(f"*{ext}"))
        files.extend(path.rglob(f"*{ext.upper()}"))
    
    # Remove duplicates and sort
    files = sorted(set(files))
    
    # Filter out example/placeholder files
    files = [f for f in files if "example" not in f.name.lower()]
    
    return files


def print_metadata(file_path: Path, metadata: DocumentMetadata) -> None:
    """Print metadata in a readable format."""
    print(f"\n📄 {file_path.name}")
    print(f"   Path: {file_path}")
    print(f"   Type: {metadata.document_type}")
    
    if metadata.sensor_type:
        print(f"   Sensor Type: {metadata.sensor_type}")
    if metadata.content_type:
        print(f"   Content Type: {metadata.content_type}")
    if metadata.algorithm_type:
        print(f"   Algorithm Type: {metadata.algorithm_type}")
    if metadata.algorithm_category:
        print(f"   Algorithm Category: {metadata.algorithm_category}")
    if metadata.regulation_type:
        print(f"   Regulation Type: {metadata.regulation_type}")
    if metadata.standard_number:
        print(f"   Standard Number: {metadata.standard_number}")
    if metadata.test_type:
        print(f"   Test Type: {metadata.test_type}")
    if metadata.test_category:
        print(f"   Test Category: {metadata.test_category}")


def print_summary(summary: Dict[str, int], total: int) -> None:
    """Print summary statistics."""
    print("\n" + "=" * 60)
    print("METADATA TAGGING SUMMARY")
    print("=" * 60)
    print(f"Total documents analyzed: {total}")
    print(f"\nDocument Types:")
    print(f"  📷 Sensor documents:     {summary['sensor_doc']:3d}")
    print(f"  🧠 Algorithm documents:  {summary['algorithm_doc']:3d}")
    print(f"  📋 Regulation documents: {summary['regulation_doc']:3d}")
    print(f"  🧪 Test documents:       {summary['test_doc']:3d}")
    print(f"  ❓ Unknown documents:    {summary['unknown']:3d}")
    print("=" * 60)


def generate_metadata_json(file_path: Path, metadata: DocumentMetadata) -> Path:
    """Generate a JSON metadata file for a document.
    
    Args:
        file_path: Path to the document
        metadata: Metadata to save
    
    Returns:
        Path to the generated JSON file
    """
    json_path = file_path.with_suffix('.metadata.json')
    
    metadata_dict = metadata.to_dict()
    metadata_dict['source_file'] = str(file_path.name)
    metadata_dict['source_path'] = str(file_path)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(metadata_dict, f, indent=2, ensure_ascii=False)
    
    return json_path


def validate_metadata(file_path: Path, tagger: ADMetadataTagger) -> bool:
    """Validate existing metadata JSON file.
    
    Args:
        file_path: Path to the document
        tagger: Metadata tagger instance
    
    Returns:
        True if metadata is valid and matches expected tags
    """
    json_path = file_path.with_suffix('.metadata.json')
    
    if not json_path.exists():
        print(f"❌ No metadata file found: {json_path}")
        return False
    
    # Load existing metadata
    with open(json_path, 'r', encoding='utf-8') as f:
        existing = json.load(f)
    
    # Generate expected metadata
    expected = tagger.tag_document(str(file_path))
    
    if expected is None:
        print(f"⚠️  Could not determine expected metadata for: {file_path}")
        return False
    
    expected_dict = expected.to_dict()
    
    # Compare
    matches = True
    for key, value in expected_dict.items():
        if key not in existing:
            print(f"❌ Missing field '{key}' in {json_path}")
            matches = False
        elif existing[key] != value:
            print(f"❌ Mismatch in '{key}': expected '{value}', got '{existing[key]}' in {json_path}")
            matches = False
    
    if matches:
        print(f"✅ Valid metadata: {json_path}")
    
    return matches


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Tag autonomous driving documents with metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--path", "-p",
        required=True,
        help="Path to file or directory to analyze"
    )
    
    parser.add_argument(
        "--summary", "-s",
        action="store_true",
        help="Show summary statistics only"
    )
    
    parser.add_argument(
        "--generate-json", "-g",
        action="store_true",
        help="Generate metadata JSON files for all documents"
    )
    
    parser.add_argument(
        "--validate", "-v",
        action="store_true",
        help="Validate existing metadata JSON files"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output"
    )
    
    args = parser.parse_args()
    
    print("[*] Autonomous Driving Document Metadata Tagger")
    print("=" * 60)
    
    # Discover documents
    try:
        path = Path(args.path)
        files = discover_documents(path)
        print(f"[INFO] Found {len(files)} document(s) to analyze")
    except FileNotFoundError as e:
        print(f"[FAIL] {e}")
        return 2
    
    if len(files) == 0:
        print("[WARN] No documents found")
        return 0
    
    # Initialize tagger
    tagger = ADMetadataTagger()
    
    # Process documents
    if args.validate:
        # Validate mode
        print("\n[INFO] Validating metadata files...")
        valid_count = 0
        for file_path in files:
            if validate_metadata(file_path, tagger):
                valid_count += 1
        
        print(f"\n[INFO] Validation complete: {valid_count}/{len(files)} valid")
        return 0 if valid_count == len(files) else 1
    
    # Tag documents
    results = tagger.tag_batch([str(f) for f in files])
    
    # Generate JSON files if requested
    if args.generate_json:
        print("\n[INFO] Generating metadata JSON files...")
        generated = 0
        for file_path in files:
            metadata = results[str(file_path)]
            if metadata:
                json_path = generate_metadata_json(file_path, metadata)
                if args.verbose:
                    print(f"   ✅ Generated: {json_path}")
                generated += 1
        print(f"[INFO] Generated {generated} metadata files")
    
    # Show detailed results if not summary mode
    if not args.summary and args.verbose:
        print("\n[INFO] Detailed Results:")
        for file_path in files:
            metadata = results[str(file_path)]
            if metadata:
                print_metadata(file_path, metadata)
            else:
                print(f"\n❓ {file_path.name}")
                print(f"   Path: {file_path}")
                print(f"   Type: Unknown (could not determine)")
    
    # Show summary
    summary = tagger.get_metadata_summary([str(f) for f in files])
    print_summary(summary, len(files))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
