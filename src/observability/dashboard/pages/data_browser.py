"""Knowledge base browser page."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.observability.dashboard.services.data_service import DataService


def render() -> None:
    """Render the medical knowledge base browser page."""
    st.header("🔍 Medical Knowledge Base")
    st.caption("查看已导入的指南、SOP、培训资料和设备手册，确认每份资料在 collection 中的落盘情况。")

    try:
        svc = DataService()
    except Exception as exc:
        st.error(f"Failed to initialise DataService: {exc}")
        return

    collections = svc.list_collections()
    if "default" not in collections:
        collections.insert(0, "default")

    collection = st.selectbox(
        "Collection",
        options=collections,
        index=0,
        key="db_collection_filter",
    )
    coll_arg = collection if collection else None

    st.divider()
    with st.expander("⚠️ Danger Zone", expanded=False):
        st.warning(
            "This will **permanently delete** all data: "
            "ChromaDB collections, BM25 indexes, images, ingestion history, and trace logs."
        )
        col_btn, _ = st.columns([1, 2])
        with col_btn:
            if st.button("🗑️ Clear All Data", type="primary", key="btn_clear_all"):
                st.session_state["confirm_clear"] = True

        if st.session_state.get("confirm_clear"):
            st.error("Are you sure? This action cannot be undone!")
            c1, c2, _ = st.columns([1, 1, 2])
            with c1:
                if st.button("✅ Yes, delete everything", key="btn_confirm_clear"):
                    result = svc.reset_all()
                    st.session_state["confirm_clear"] = False
                    if result["errors"]:
                        st.warning(
                            f"Cleared with {len(result['errors'])} error(s): "
                            + "; ".join(result["errors"])
                        )
                    else:
                        st.success(
                            f"All data cleared! "
                            f"{result['collections_deleted']} collection(s) deleted."
                        )
                    st.rerun()
            with c2:
                if st.button("❌ Cancel", key="btn_cancel_clear"):
                    st.session_state["confirm_clear"] = False
                    st.rerun()

    st.divider()

    try:
        docs = svc.list_documents(coll_arg)
    except Exception as exc:
        st.error(f"Failed to load documents: {exc}")
        return

    if not docs:
        st.info(
            "**No documents found in this collection.** "
            "Use the Ingestion Center page to upload and ingest files, "
            "or select a different collection from the dropdown above."
        )
        return

    st.subheader(f"📫 Documents ({len(docs)})")

    for idx, doc in enumerate(docs):
        source_name = Path(doc["source_path"]).name
        label = (
            f"📄 {source_name}  -  {doc['chunk_count']} chunks / "
            f"{doc['image_count']} images"
        )
        with st.expander(label, expanded=(len(docs) == 1)):
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Chunks", doc["chunk_count"])
            col_b.metric("Images", doc["image_count"])
            col_c.metric("Collection", doc.get("collection", "-"))
            st.caption(
                f"**Source:** {doc['source_path']}  /  "
                f"**Hash:** `{doc['source_hash'][:16]}...`  /  "
                f"**Processed:** {doc.get('processed_at', '-')}"
            )

            st.divider()

            chunks = svc.get_chunks(doc["source_hash"], coll_arg)
            if chunks:
                st.markdown(f"### 🧩 Chunks ({len(chunks)})")
                for cidx, chunk in enumerate(chunks):
                    text = chunk.get("text", "")
                    meta = chunk.get("metadata", {})
                    chunk_id = chunk["id"]

                    title = meta.get("title", "")
                    if not title:
                        title = text[:60].replace("\n", " ").strip()
                        if len(text) > 60:
                            title += "..."

                    with st.container(border=True):
                        st.markdown(
                            f"**Chunk {cidx + 1}** / `{chunk_id[-16:]}` / "
                            f"{len(text)} chars"
                        )
                        st.text_area(
                            "Content",
                            value=text,
                            height=max(120, min(len(text) // 2, 600)),
                            disabled=True,
                            key=f"chunk_text_{idx}_{cidx}",
                            label_visibility="collapsed",
                        )
                        with st.expander("Metadata", expanded=False):
                            st.json(meta)
            else:
                st.caption("No chunks found in vector store for this document.")

            images = svc.get_images(doc["source_hash"], coll_arg)
            if images:
                st.divider()
                st.markdown(f"### 🖼️ Images ({len(images)})")
                img_cols = st.columns(min(len(images), 4))
                for iidx, img in enumerate(images):
                    with img_cols[iidx % len(img_cols)]:
                        img_path = Path(img.get("file_path", ""))
                        if img_path.exists():
                            st.image(str(img_path), caption=img["image_id"], width=200)
                        else:
                            st.caption(f"{img['image_id']} (file missing)")
