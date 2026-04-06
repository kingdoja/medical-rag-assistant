"""Medical Demo Evaluation Panel – specialized evaluation for medical assistant demo.

This page provides evaluation specifically for the 12-question medical demo
standard test set, with visualizations tailored for interview presentation.

Layout:
1. Demo overview: collection info, test set summary
2. Quick evaluation: run P0 scenarios only
3. Results visualization: hit rate, citation rate, boundary validation
4. Scenario breakdown: per-scenario results with pass/fail indicators
5. Demo readiness indicator: overall health check for interview
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

logger = logging.getLogger(__name__)

# Medical demo test set location
MEDICAL_TEST_SET_PATH = Path("tests/fixtures/medical_demo_test_set.json")
COLLECTION_NAME = "medical_demo_v01"

# Evaluation thresholds (from test suite)
MIN_HIT_RATE_P0 = 1.0  # 100% for P0
MIN_HIT_RATE_P1 = 0.6  # 60% for P1
MIN_CITATION_RATE = 0.7  # 70%
MIN_REFUSAL_ACCURACY = 1.0  # 100%


def render() -> None:
    """Render the Medical Demo Evaluation Panel page."""
    st.header("🏥 Medical Demo Evaluation")
    st.markdown(
        "专门用于 **PathoMind 医疗知识与质控助手** 的 12 题标准演示题集评估。"
        "此面板提供面试演示就绪度检查和详细的场景验证结果。"
    )

    # ── Demo Overview ──────────────────────────────────────────────
    _render_demo_overview()

    st.divider()

    # ── Quick Evaluation Controls ──────────────────────────────────
    st.subheader("⚙️ Evaluation Controls")

    col1, col2 = st.columns([2, 1])

    with col1:
        eval_mode = st.radio(
            "Evaluation Mode",
            options=["P0 Only (Fast)", "P1 Only (Advanced)", "All Scenarios (Complete)"],
            index=0,
            key="medical_eval_mode",
            help="P0 scenarios are core demo questions. P1 scenarios test advanced multi-document reasoning. Complete mode includes all 12 scenarios.",
        )

    with col2:
        top_k = st.number_input(
            "Top-K",
            min_value=1,
            max_value=20,
            value=10,
            key="medical_eval_top_k",
            help="Number of chunks to retrieve per query.",
        )

    # Run button
    run_clicked = st.button(
        "▶️  Run Evaluation",
        type="primary",
        key="medical_eval_run_btn",
        disabled=not MEDICAL_TEST_SET_PATH.exists(),
    )

    if run_clicked:
        p0_only = eval_mode.startswith("P0")
        p1_only = eval_mode.startswith("P1")
        _run_medical_evaluation(p0_only=p0_only, p1_only=p1_only, top_k=int(top_k))

    st.divider()

    # ── Results Display ────────────────────────────────────────────
    if "medical_eval_results" in st.session_state:
        _render_evaluation_results(st.session_state["medical_eval_results"])


def _render_demo_overview() -> None:
    """Display demo collection and test set overview."""
    st.subheader("📋 Demo Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Collection",
            value=COLLECTION_NAME,
            help="Target collection for medical demo evaluation",
        )

    with col2:
        # Load test set to count scenarios
        if MEDICAL_TEST_SET_PATH.exists():
            try:
                with MEDICAL_TEST_SET_PATH.open("r", encoding="utf-8") as f:
                    test_data = json.load(f)
                total_scenarios = len(test_data.get("test_cases", []))
                p0_scenarios = len([
                    tc for tc in test_data.get("test_cases", [])
                    if tc.get("priority") == "P0"
                ])
                st.metric(
                    label="Total Scenarios",
                    value=f"{total_scenarios} ({p0_scenarios} P0)",
                    help="Total test scenarios in the medical demo set",
                )
            except Exception as exc:
                st.metric(label="Total Scenarios", value="—")
                logger.warning(f"Failed to load test set: {exc}")
        else:
            st.metric(label="Total Scenarios", value="—")
            st.warning(f"⚠️ Test set not found: {MEDICAL_TEST_SET_PATH}")

    with col3:
        # Show demo flow scenarios
        demo_flow = "S1 → S2 → S4 → S7 → S12"
        st.metric(
            label="Demo Flow",
            value="5 scenarios",
            delta=demo_flow,
            help="Standard 3-minute demo flow",
        )

    # Show test set info
    if MEDICAL_TEST_SET_PATH.exists():
        st.caption(f"📄 Test Set: `{MEDICAL_TEST_SET_PATH}`")
    else:
        st.error(
            f"❌ **Test set not found:** `{MEDICAL_TEST_SET_PATH}`. "
            "Run the test suite setup to generate the medical demo test set."
        )


def _run_medical_evaluation(p0_only: bool, p1_only: bool, top_k: int) -> None:
    """Execute medical demo evaluation and store results in session state."""
    with st.spinner("Running medical demo evaluation…"):
        try:
            results = _execute_medical_evaluation(p0_only=p0_only, p1_only=p1_only, top_k=top_k)
            st.session_state["medical_eval_results"] = results
            st.success("✅ Evaluation complete!")
        except Exception as exc:
            st.error(f"❌ Evaluation failed: {exc}")
            logger.exception("Medical evaluation failed")


def _execute_medical_evaluation(p0_only: bool, p1_only: bool, top_k: int) -> Dict[str, Any]:
    """Run the medical demo evaluation pipeline.

    Returns:
        Dict with evaluation results including:
        - summary: aggregate metrics
        - scenarios: per-scenario results
        - demo_readiness: overall health check
        - p0_readiness: P0 scenario readiness
        - p1_readiness: P1 scenario readiness
    """
    from src.core.settings import load_settings
    from src.core.query_engine.hybrid_search import HybridSearch

    # Load test set
    with MEDICAL_TEST_SET_PATH.open("r", encoding="utf-8") as f:
        test_data = json.load(f)

    test_cases = test_data["test_cases"]

    if p0_only:
        test_cases = [tc for tc in test_cases if tc.get("priority") == "P0"]
    elif p1_only:
        test_cases = [tc for tc in test_cases if tc.get("priority") == "P1"]

    # Initialize search engine
    settings = load_settings()
    search = HybridSearch(settings)

    # Run evaluation
    scenario_results = []
    hit_count = 0
    retrieval_case_count = 0

    start_time = time.time()

    for tc in test_cases:
        scenario_id = tc["scenario_id"]
        query = tc["query"]
        expected_sources = tc.get("expected_sources", [])
        validation_type = tc.get("validation_type")
        priority = tc.get("priority", "P1")

        # Skip boundary scenarios for retrieval evaluation
        if validation_type in ["response_boundary", "response_content"]:
            scenario_results.append({
                "scenario_id": scenario_id,
                "scenario_name": tc["scenario_name"],
                "query": query,
                "priority": priority,
                "validation_type": validation_type,
                "status": "skipped",
                "reason": "Boundary/content validation (not retrieval-based)",
            })
            continue

        retrieval_case_count += 1

        try:
            # Run search
            search_results = search.search(query=query, top_k=top_k)

            # Check source hit
            hit = _check_source_hit(search_results, expected_sources)

            if hit:
                hit_count += 1

            # Extract top sources
            top_sources = []
            for result in search_results[:3]:
                if hasattr(result, 'metadata') and isinstance(result.metadata, dict):
                    source = result.metadata.get('source', '')
                elif isinstance(result, dict):
                    source = result.get('metadata', {}).get('source', '')
                else:
                    continue

                if source:
                    top_sources.append(Path(source).name)

            scenario_results.append({
                "scenario_id": scenario_id,
                "scenario_name": tc["scenario_name"],
                "query": query,
                "priority": priority,
                "expected_sources": expected_sources,
                "top_sources": top_sources,
                "hit": hit,
                "num_results": len(search_results),
                "status": "pass" if hit else "fail",
            })

        except Exception as exc:
            logger.error(f"Search failed for {scenario_id}: {exc}")
            scenario_results.append({
                "scenario_id": scenario_id,
                "scenario_name": tc["scenario_name"],
                "query": query,
                "priority": priority,
                "error": str(exc),
                "status": "error",
            })

    elapsed_time = time.time() - start_time

    # Calculate metrics
    hit_rate = hit_count / retrieval_case_count if retrieval_case_count > 0 else 0.0
    
    # Calculate per-priority metrics
    p0_scenarios = [s for s in scenario_results if s.get("priority") == "P0"]
    p1_scenarios = [s for s in scenario_results if s.get("priority") == "P1"]
    
    p0_retrieval = [s for s in p0_scenarios if s.get("status") in ["pass", "fail"]]
    p1_retrieval = [s for s in p1_scenarios if s.get("status") in ["pass", "fail"]]
    
    p0_hit_count = len([s for s in p0_retrieval if s.get("hit", False)])
    p1_hit_count = len([s for s in p1_retrieval if s.get("hit", False)])
    
    p0_hit_rate = p0_hit_count / len(p0_retrieval) if p0_retrieval else 0.0
    p1_hit_rate = p1_hit_count / len(p1_retrieval) if p1_retrieval else 0.0

    # Determine readiness
    p0_ready = p0_hit_rate >= MIN_HIT_RATE_P0 if p0_retrieval else True
    p1_ready = p1_hit_rate >= MIN_HIT_RATE_P1 if p1_retrieval else True
    demo_ready = p0_ready and (p1_ready if p1_retrieval else True)
    
    # Determine priority mode
    priority_mode = "P0" if p0_only else ("P1" if p1_only else "All")

    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "p0_only": p0_only,
        "p1_only": p1_only,
        "priority_mode": priority_mode,
        "top_k": top_k,
        "total_scenarios": len(test_cases),
        "retrieval_scenarios": retrieval_case_count,
        "hit_count": hit_count,
        "hit_rate": hit_rate,
        "p0_hit_count": p0_hit_count,
        "p0_hit_rate": p0_hit_rate,
        "p0_retrieval_count": len(p0_retrieval),
        "p1_hit_count": p1_hit_count,
        "p1_hit_rate": p1_hit_rate,
        "p1_retrieval_count": len(p1_retrieval),
        "elapsed_time": elapsed_time,
        "demo_ready": demo_ready,
        "p0_ready": p0_ready,
        "p1_ready": p1_ready,
        "scenarios": scenario_results,
    }


def _check_source_hit(results: List[Any], expected_sources: List[str]) -> bool:
    """Check if any expected source appears in retrieved results."""
    if not expected_sources:
        return True

    retrieved_sources = set()
    for result in results:
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
    return bool(expected_set & retrieved_sources)


def _render_evaluation_results(results: Dict[str, Any]) -> None:
    """Display evaluation results with medical demo specific visualizations."""
    st.subheader("📊 Evaluation Results")

    # ── Demo Readiness Indicator ───────────────────────────────────
    demo_ready = results.get("demo_ready", False)
    p0_ready = results.get("p0_ready", False)
    p1_ready = results.get("p1_ready", False)
    priority_mode = results.get("priority_mode", "All")

    # Overall readiness
    if demo_ready:
        st.success(
            "✅ **Demo Ready!** Hit rate meets the minimum threshold for interview presentation.",
            icon="🎯",
        )
    else:
        st.error(
            "❌ **Demo Not Ready.** Hit rate below threshold. Review failed scenarios below.",
            icon="⚠️",
        )
    
    # Per-priority readiness indicators
    col1, col2 = st.columns(2)
    
    with col1:
        p0_hit_rate = results.get("p0_hit_rate", 0.0)
        p0_retrieval_count = results.get("p0_retrieval_count", 0)
        if p0_retrieval_count > 0:
            if p0_ready:
                st.success(f"✅ **P0 Ready** ({p0_hit_rate:.1%} hit rate, threshold: {MIN_HIT_RATE_P0:.0%})")
            else:
                st.error(f"❌ **P0 Not Ready** ({p0_hit_rate:.1%} hit rate, threshold: {MIN_HIT_RATE_P0:.0%})")
        else:
            st.info("ℹ️ No P0 scenarios evaluated")
    
    with col2:
        p1_hit_rate = results.get("p1_hit_rate", 0.0)
        p1_retrieval_count = results.get("p1_retrieval_count", 0)
        if p1_retrieval_count > 0:
            if p1_ready:
                st.success(f"✅ **P1 Ready** ({p1_hit_rate:.1%} hit rate, threshold: {MIN_HIT_RATE_P1:.0%})")
            else:
                st.error(f"❌ **P1 Not Ready** ({p1_hit_rate:.1%} hit rate, threshold: {MIN_HIT_RATE_P1:.0%})")
        else:
            st.info("ℹ️ No P1 scenarios evaluated")

    st.divider()

    # ── Summary Metrics ────────────────────────────────────────────
    st.subheader("📈 Summary Metrics")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        hit_rate = results.get("hit_rate", 0.0)
        hit_rate_pct = hit_rate * 100
        priority_mode = results.get("priority_mode", "All")
        threshold = MIN_HIT_RATE_P0 if priority_mode == "P0" else MIN_HIT_RATE_P1
        delta_color = "normal" if hit_rate >= threshold else "inverse"
        st.metric(
            label="Overall Hit Rate",
            value=f"{hit_rate_pct:.1f}%",
            delta=f"Threshold: {threshold * 100:.0f}%",
            delta_color=delta_color,
        )

    with col2:
        p0_hit_rate = results.get("p0_hit_rate", 0.0)
        p0_retrieval_count = results.get("p0_retrieval_count", 0)
        if p0_retrieval_count > 0:
            st.metric(
                label="P0 Hit Rate",
                value=f"{p0_hit_rate * 100:.1f}%",
                delta=f"{results.get('p0_hit_count', 0)}/{p0_retrieval_count}",
            )
        else:
            st.metric(label="P0 Hit Rate", value="—")

    with col3:
        p1_hit_rate = results.get("p1_hit_rate", 0.0)
        p1_retrieval_count = results.get("p1_retrieval_count", 0)
        if p1_retrieval_count > 0:
            st.metric(
                label="P1 Hit Rate",
                value=f"{p1_hit_rate * 100:.1f}%",
                delta=f"{results.get('p1_hit_count', 0)}/{p1_retrieval_count}",
            )
        else:
            st.metric(label="P1 Hit Rate", value="—")

    with col4:
        elapsed = results.get("elapsed_time", 0.0)
        st.metric(
            label="Evaluation Time",
            value=f"{elapsed:.1f}s",
            help="Total time to run all scenarios",
        )

    with col5:
        total = results.get("total_scenarios", 0)
        mode_label = priority_mode
        st.metric(
            label="Mode",
            value=mode_label,
            delta=f"{total} scenarios",
        )

    st.caption(
        f"🕒 Timestamp: {results.get('timestamp', '—')} · "
        f"Top-K: {results.get('top_k', 10)}"
    )

    st.divider()

    # ── Scenario Breakdown ─────────────────────────────────────────
    st.subheader("🔍 Scenario Breakdown")

    scenarios = results.get("scenarios", [])

    if not scenarios:
        st.info("No scenario results available.")
        return

    # Group by priority and status
    p0_scenarios = [s for s in scenarios if s.get("priority") == "P0"]
    p1_scenarios = [s for s in scenarios if s.get("priority") == "P1"]
    
    passed = [s for s in scenarios if s.get("status") == "pass"]
    failed = [s for s in scenarios if s.get("status") == "fail"]
    skipped = [s for s in scenarios if s.get("status") == "skipped"]
    errors = [s for s in scenarios if s.get("status") == "error"]

    # Show tabs for different views
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        f"📋 All ({len(scenarios)})",
        f"🎯 P0 ({len(p0_scenarios)})",
        f"🚀 P1 ({len(p1_scenarios)})",
        f"✅ Passed ({len(passed)})",
        f"❌ Failed ({len(failed)})",
        f"⚠️ Other ({len(skipped) + len(errors)})",
    ])

    with tab1:
        if scenarios:
            for scenario in scenarios:
                _render_scenario_card(scenario, status=scenario.get("status", "unknown"))
        else:
            st.info("No scenarios.")

    with tab2:
        if p0_scenarios:
            st.markdown("**P0 scenarios are core demo questions with 100% hit rate requirement.**")
            for scenario in p0_scenarios:
                _render_scenario_card(scenario, status=scenario.get("status", "unknown"))
        else:
            st.info("No P0 scenarios.")

    with tab3:
        if p1_scenarios:
            st.markdown("**P1 scenarios test advanced multi-document reasoning with 60% hit rate requirement.**")
            for scenario in p1_scenarios:
                _render_scenario_card(scenario, status=scenario.get("status", "unknown"))
        else:
            st.info("No P1 scenarios.")

    with tab4:
        if passed:
            for scenario in passed:
                _render_scenario_card(scenario, status="pass")
        else:
            st.info("No passed scenarios.")

    with tab5:
        if failed:
            for scenario in failed:
                _render_scenario_card(scenario, status="fail")
        else:
            st.info("No failed scenarios.")

    with tab6:
        if skipped:
            st.markdown("**Skipped Scenarios:**")
            for scenario in skipped:
                _render_scenario_card(scenario, status="skipped")
        if errors:
            st.markdown("**Error Scenarios:**")
            for scenario in errors:
                _render_scenario_card(scenario, status="error")
        if not skipped and not errors:
            st.info("No skipped or error scenarios.")


def _render_scenario_card(scenario: Dict[str, Any], status: str) -> None:
    """Render a single scenario result card."""
    scenario_id = scenario.get("scenario_id", "—")
    scenario_name = scenario.get("scenario_name", "—")
    query = scenario.get("query", "—")
    priority = scenario.get("priority", "—")

    # Status icon
    status_icons = {
        "pass": "✅",
        "fail": "❌",
        "skipped": "⏭️",
        "error": "⚠️",
    }
    icon = status_icons.get(status, "❓")

    # Expander label
    label = f"{icon} **{scenario_id}** ({priority}): {scenario_name}"

    with st.expander(label, expanded=(status == "fail")):
        st.markdown(f"**Query:** {query}")

        if status == "skipped":
            reason = scenario.get("reason", "—")
            st.info(f"ℹ️ {reason}")

        elif status == "error":
            error = scenario.get("error", "—")
            st.error(f"❌ Error: {error}")

        elif status in ["pass", "fail"]:
            expected = scenario.get("expected_sources", [])
            top_sources = scenario.get("top_sources", [])
            num_results = scenario.get("num_results", 0)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Expected Sources:**")
                if expected:
                    for src in expected:
                        st.markdown(f"- `{src}`")
                else:
                    st.caption("(No specific source requirement)")

            with col2:
                st.markdown(f"**Top 3 Retrieved:** ({num_results} total)")
                if top_sources:
                    for src in top_sources:
                        # Highlight if it matches expected
                        if src in expected:
                            st.markdown(f"- ✅ `{src}`")
                        else:
                            st.markdown(f"- `{src}`")
                else:
                    st.caption("(No results)")

            # Show hit status
            if status == "pass":
                st.success("✅ At least one expected source found in top-k results.")
            else:
                st.error("❌ No expected sources found in top-k results.")
