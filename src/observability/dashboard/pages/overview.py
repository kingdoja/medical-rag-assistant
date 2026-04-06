"""Medical demo overview page."""

from __future__ import annotations

from typing import Any, Dict

import streamlit as st

from src.observability.dashboard.services.config_service import ConfigService


def _safe_collection_stats() -> Dict[str, Any]:
    """Attempt to load collection statistics from ChromaDB."""
    try:
        import chromadb
        from chromadb.config import Settings as ChromaSettings

        from src.core.settings import load_settings, resolve_path

        settings = load_settings()
        persist_dir = str(resolve_path(settings.vector_store.persist_directory))
        client = chromadb.PersistentClient(
            path=persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True),
        )

        stats: Dict[str, Any] = {}
        for col in client.list_collections():
            name = col.name if hasattr(col, "name") else str(col)
            collection = client.get_collection(name)
            stats[name] = {"chunk_count": collection.count()}
        return stats
    except Exception:
        return {}


def render() -> None:
    """Render the PathoMind medical demo overview page."""
    st.header("🩺 PathoMind Medical Demo")
    st.caption(
        "面向病理科 / 检验科内部知识管理、培训问答与流程质控场景的知识助手。"
        "这里优先展示演示 readiness、资料范围和系统边界。"
    )

    st.markdown(
        """
**当前定位**
- 资料类型：指南、SOP、培训材料、设备手册
- 核心能力：真实 ingest、中文检索、引用可追溯
- 风险边界：不做自动诊断，不输出高风险临床结论
"""
    )

    stats = _safe_collection_stats()

    from src.core.settings import resolve_path

    traces_path = resolve_path("logs/traces.jsonl")
    trace_count = 0
    if traces_path.exists():
        trace_count = sum(1 for _ in traces_path.open(encoding="utf-8"))

    medical_collection = stats.get("medical_demo_v01", {})
    chunk_count = medical_collection.get("chunk_count", "?")

    top_cols = st.columns(4)
    with top_cols[0]:
        st.metric("Demo Collection", "medical_demo_v01")
    with top_cols[1]:
        st.metric("Indexed Chunks", chunk_count)
    with top_cols[2]:
        st.metric("Collections", len(stats))
    with top_cols[3]:
        st.metric("Recorded Traces", trace_count)

    st.markdown(
        """
**推荐 3 分钟演示链路**
1. `S1`：展示 SOP / 规范可检索且有依据
2. `S4` 或 `S5`：展示设备 / 图文资料不是只会回 WHO 指南
3. `S7`：展示边界能力，拒绝诊断类请求并拉回资料范围
"""
    )

    st.subheader("🔧 Medical Demo Configuration")

    try:
        config_service = ConfigService()
        cards = config_service.get_component_cards()
    except Exception as exc:
        st.error(f"Failed to load configuration: {exc}")
        return

    cols = st.columns(min(len(cards), 3))
    for idx, card in enumerate(cards):
        with cols[idx % len(cols)]:
            st.markdown(f"**{card.name}**")
            st.caption(f"Provider: `{card.provider}`  \nModel: `{card.model}`")
            with st.expander("Details"):
                for key, value in card.extra.items():
                    st.text(f"{key}: {value}")

    st.subheader("📁 Knowledge Collections")

    if stats:
        stat_cols = st.columns(min(len(stats), 4))
        for idx, (name, info) in enumerate(sorted(stats.items())):
            with stat_cols[idx % len(stat_cols)]:
                count = info.get("chunk_count", "?")
                st.metric(label=name, value=count)
                if name == "medical_demo_v01":
                    st.caption("Primary medical demo collection")
                elif count in (0, "?"):
                    st.caption("⚠️ Empty")
    else:
        st.warning(
            "**No collections found or ChromaDB unavailable.** "
            "Go to the Ingestion Center page to upload and ingest documents."
        )

    st.subheader("📈 Trace Activity")
    if trace_count > 0:
        st.metric("Total traces", trace_count)
    else:
        st.info("No traces recorded yet. Run an ingestion or query first.")
