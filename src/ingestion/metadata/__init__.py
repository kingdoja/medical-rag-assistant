"""Metadata tagging module for autonomous driving documents."""

from src.ingestion.metadata.ad_metadata_tagger import (
    ADMetadataTagger,
    DocumentMetadata,
    create_metadata_tagger,
)

__all__ = [
    "ADMetadataTagger",
    "DocumentMetadata",
    "create_metadata_tagger",
]
