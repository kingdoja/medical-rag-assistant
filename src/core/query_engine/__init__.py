"""
Query Engine Module.

This package contains the hybrid search engine components:
- Query preprocessing
- Query analysis (complexity and intent detection)
- Dense retrieval (embedding-based)
- Sparse retrieval (BM25)
- Result fusion (RRF)
- Reranking
- Knowledge base scope awareness
"""

from src.core.query_engine.query_processor import (
    QueryProcessor,
    QueryProcessorConfig,
    create_query_processor,
    DEFAULT_STOPWORDS,
    CHINESE_STOPWORDS,
    ENGLISH_STOPWORDS,
)
from src.core.query_engine.query_analyzer import (
    QueryAnalyzer,
    QueryAnalysis,
    create_query_analyzer,
)
from src.core.query_engine.dense_retriever import (
    DenseRetriever,
    create_dense_retriever,
)
from src.core.query_engine.sparse_retriever import (
    SparseRetriever,
    create_sparse_retriever,
)
from src.core.query_engine.fusion import (
    RRFFusion,
    rrf_score,
)
from src.core.query_engine.hybrid_search import (
    HybridSearch,
    HybridSearchConfig,
    HybridSearchResult,
    create_hybrid_search,
)
from src.core.query_engine.document_grouper import (
    DocumentGrouper,
    DocumentGroup,
    create_document_grouper,
)
from src.core.query_engine.scope_provider import (
    ScopeProvider,
    ScopeInfo,
)

__all__ = [
    "QueryProcessor",
    "QueryProcessorConfig",
    "create_query_processor",
    "DEFAULT_STOPWORDS",
    "CHINESE_STOPWORDS",
    "ENGLISH_STOPWORDS",
    "QueryAnalyzer",
    "QueryAnalysis",
    "create_query_analyzer",
    "DenseRetriever",
    "create_dense_retriever",
    "SparseRetriever",
    "create_sparse_retriever",
    "RRFFusion",
    "rrf_score",
    "HybridSearch",
    "HybridSearchConfig",
    "HybridSearchResult",
    "create_hybrid_search",
    "DocumentGrouper",
    "DocumentGroup",
    "create_document_grouper",
    "ScopeProvider",
    "ScopeInfo",
]
