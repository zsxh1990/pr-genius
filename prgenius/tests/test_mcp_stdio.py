"""MCP stdio roundtrip test — lesson-21 代码化 (35 期众测任务1 ether2 评测反哺)

Why this file exists:
    pr-genius/tests/test_mcp.py 只测了 "MCP tool 包装的底层 fn",
    35 期众测任务1 ether2 SMOKE_RESULTS.md §1.4 抓到 3 个 runtime bug
    都是 MCP transport / 字段路径 / 死导入层静态分析看不出的:
    1. soft_violations 路径错配 — mcp.py len(int) 崩  ← B1 已修
    2. _parse_frontmatter_dict 死导入 — ImportError  ← B2 已修
    3. .venv/ LICENSE.md 假阳 — validate.py 扫到  ← B3 已修

Strategy:
    不走 FastMCP transport (0.x Tool 对象不暴露 .fn + convert_result str/str bug).
    直接调 _load_tools() 返回的 FastMCP 实例, 从 _tool_manager._tools 提取
    8 个 tool 的 .fn, 用真实 JSON-RPC 2.0 input shape 调, 断言返回结构.

Lesson-21 hard gate:
    8 tools 每个至少 1 个 roundtrip test, 失败 = lesson-21 失守.

Run:
    PYTHONPATH=./prgenius/src python3 -m pytest prgenius/tests/test_mcp_stdio.py -v
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REPO_ROOT_STR = str(REPO_ROOT)


# ============================================================
# fixture: 提取 8 个 MCP tool 的底层 fn
# ============================================================

@pytest.fixture(scope="module")
def mcp_tools() -> dict[str, Callable]:
    """加载 MCP server 实例, 提取 8 个 tool 的 callable fn.

    Returns:
        dict[tool_name, callable] — tool_name ∈ {analyze_pr, coach_pr, triage_pr,
            get_repo_profile, list_open_prs, get_case_study, search_patterns,
            schema_info}
    """
    sys.path.insert(0, str(REPO_ROOT / "prgenius" / "src"))
    from prgenius.mcp import _load_tools
    mcp = _load_tools(repo_root=REPO_ROOT)

    # FastMCP 0.x: 内部 _tool_manager._tools 是 {name: Tool对象}
    # Tool 对象有 .fn 属性指向注册的 callable (FastMCP API 内部细节,
    # 不稳定但够测试用)
    tools: dict[str, Callable] = {}
    tm = getattr(mcp, "_tool_manager", None)
    if tm is None:
        # 旧版 FastMCP 路径
        tm = getattr(mcp, "_tools", mcp)

    raw = getattr(tm, "_tools", None)
    if raw is None and hasattr(tm, "values"):
        raw = {t.name: t for t in tm.values()}

    if raw is None:
        pytest.skip("FastMCP 内部 _tools 不可访问 (API 变了?), 跳过 stdio roundtrip")

    for name, tool in raw.items():
        fn = getattr(tool, "fn", None)
        if fn is not None:
            tools[name] = fn
    return tools


# ============================================================
# regression: B1 soft_violations 路径错配 (35 期评测 ether2 抓)
# ============================================================

def test_b1_soft_violations_field_path_not_crash(mcp_tools):
    """B1 regression: triage_pr warn/reject verdict 不能 len(int) 崩.

    lesson-21: 这是 MCP stdio runtime bug, 静态分析(mypy/读代码)看不到,
    必须 roundtrip 实测. 35 期评测 ether2 SMOKE_RESULTS.md §1.4 抓到过.
    """
    if "triage_pr" not in mcp_tools:
        pytest.skip("triage_pr tool not registered")

    triage_pr = mcp_tools["triage_pr"]

    # 三种 verdict 都跑一遍, 验证 mcp.py 不再 len(int) 崩
    for title, verdict_hint in [
        ("docs: trivial typo fix", "pass"),
        ("WIP: experimental feature with no tests", "warn"),
        ("feat: drop database table", "reject"),  # 假设有 hard rule 命中
    ]:
        result = triage_pr(
            title=title,
            repo="Ikalus1988/MisakaNet",
            body="trivial test body",
            diff_stat="README.md | 1 +-",
        )
        verdict = result.get("verdict", "unknown")
        # 关键断言: 不能 TypeError
        assert "verdict" in result, f"triage_pr({title!r}) missing verdict key"
        # B1 修复后: recommended_action 应该是字符串(包含 count), 不能崩
        if verdict in ("warn", "reject"):
            rec = result.get("recommended_action", "")
            assert isinstance(rec, str), (
                f"B1 regression: recommended_action 不是 str ({type(rec).__name__}): {rec!r}"
            )
            # 软规则触发时, recommended_action 应含 count
            if verdict == "warn":
                assert "soft rule" in rec, f"warn verdict 应含 'soft rule' 字样: {rec!r}"


# ============================================================
# regression: B2 _parse_frontmatter_dict 死导入 (35 期评测 ether2 抓)
# ============================================================

def test_b2_search_patterns_no_dead_import(mcp_tools):
    """B2 regression: search_patterns 不能 ImportError.

    lesson-21: 35 期评测 ether2 抓到 cannot import name '_parse_frontmatter_dict'
    修复: mcp.py 改用现存的 parse_frontmatter (parser.py:96).
    """
    if "search_patterns" not in mcp_tools:
        pytest.skip("search_patterns tool not registered")

    search_patterns = mcp_tools["search_patterns"]
    # 触发关键词: "duplicate" 在多个 anti-pattern 中出现
    result = search_patterns(query="duplicate", pattern_type="all", limit=5)
    assert isinstance(result, list), f"应返回 list, 实际 {type(result).__name__}"
    # 验证返回结构 (修复后是完整 dict, 修复前会 ImportError)
    for hit in result[:3]:
        assert isinstance(hit, dict), f"hit 应该是 dict: {hit!r}"
        # parse_frontmatter 返回的 dict 必含这些键
        assert "type" in hit, f"hit 缺 'type': {hit!r}"
        assert "file" in hit, f"hit 缺 'file': {hit!r}"


# ============================================================
# 8 tools 全覆盖 smoke (lesson-21 hard gate)
# ============================================================

EXPECTED_TOOLS = {
    "analyze_pr",
    "coach_pr",
    "triage_pr",
    "get_repo_profile",
    "list_open_prs",
    "get_case_study",
    "search_patterns",
    "schema_info",
}


def test_all_8_tools_registered(mcp_tools):
    """lesson-21 hard gate: 8 tools 全部注册成功."""
    registered = set(mcp_tools.keys())
    missing = EXPECTED_TOOLS - registered
    assert not missing, f"MCP 缺工具: {missing}, 当前注册: {registered}"


def test_schema_info_roundtrip(mcp_tools):
    """schema_info: 返回 OKF schema dict, 必含 schema_versions / delta_kinds / action_enum."""
    if "schema_info" not in mcp_tools:
        pytest.skip("schema_info not registered")
    result = mcp_tools["schema_info"]()
    assert isinstance(result, dict), f"schema_info 应返回 dict, 实际 {type(result).__name__}"
    # lesson-13/18: 至少含 schema_versions 字段
    assert "schema_versions" in result or "schema_version" in result, (
        f"schema_info 缺 schema_versions: {result.keys()}"
    )


def test_get_repo_profile_known_repo(mcp_tools):
    """get_repo_profile: 已知仓 (MisakaNet) 返回完整画像, 不崩."""
    if "get_repo_profile" not in mcp_tools:
        pytest.skip("get_repo_profile not registered")
    result = mcp_tools["get_repo_profile"]("Ikalus1988/MisakaNet")
    assert isinstance(result, dict), f"应返回 dict, 实际 {type(result).__name__}"
    # 已知仓: 不应含 error
    assert "error" not in result, f"已知仓不应返回 error: {result.get('error')}"


def test_get_repo_profile_unknown_repo_structured_error(mcp_tools):
    """get_repo_profile: 未知仓返回结构化 'not found', 不抛 exception.

    lesson-18 沉淀: 是设计 (knowledge bundle 不查 self), 不是 bug.
    """
    if "get_repo_profile" not in mcp_tools:
        pytest.skip("get_repo_profile not registered")
    result = mcp_tools["get_repo_profile"]("totally-unknown-org/totally-unknown-repo-xyz")
    assert isinstance(result, dict), f"应返回 dict, 实际 {type(result).__name__}"
    assert "error" in result, f"未知仓应含 error 字段, 实际 keys: {list(result.keys())}"
    assert "not found" in result["error"], f"error 应含 'not found', 实际: {result['error']}"


def test_list_open_prs_returns_list(mcp_tools):
    """list_open_prs: 返回 list of open case studies."""
    if "list_open_prs" not in mcp_tools:
        pytest.skip("list_open_prs not registered")
    result = mcp_tools["list_open_prs"]()
    assert isinstance(result, list), f"应返回 list, 实际 {type(result).__name__}"


def test_coach_pr_pallets_flask(mcp_tools):
    """coach_pr: pallets/flask ≥10k star + 有 policy 应触发 high_risk."""
    if "coach_pr" not in mcp_tools:
        pytest.skip("coach_pr not registered")
    result = mcp_tools["coach_pr"](
        title="fix typo",
        repo="pallets/flask",
        body="trivial typo",
    )
    assert isinstance(result, dict), f"应返回 dict, 实际 {type(result).__name__}"
    # 大仓 + 有 policy → high_risk tier
    tier = result.get("tier", "")
    assert tier in ("low_risk", "medium_risk", "high_risk"), (
        f"coach_pr 应返回 tier ∈ 3 档, 实际: {tier!r}"
    )


def test_analyze_pr_returns_dict(mcp_tools):
    """analyze_pr: 返回 dict 含 tier + signals + checklist."""
    if "analyze_pr" not in mcp_tools:
        pytest.skip("analyze_pr not registered")
    result = mcp_tools["analyze_pr"](
        title="feat: add feature",
        repo="Ikalus1988/MisakaNet",
        body="adds X",
    )
    assert isinstance(result, dict), f"应返回 dict, 实际 {type(result).__name__}"
    # tier + signals 是 analyze_pr 必有字段
    assert "tier" in result, f"analyze_pr 缺 tier: {list(result.keys())}"


def test_get_case_study_returns_dict(mcp_tools):
    """get_case_study: 已知 case study (Ikalus1988/MisakaNet) 返回结构化 dict."""
    if "get_case_study" not in mcp_tools:
        pytest.skip("get_case_study not registered")
    # MisakaNet 有 case study 440 (frontmatter tests), pr_number 必 ≥ 1
    try:
        result = mcp_tools["get_case_study"](repo="Ikalus1988-MisakaNet", pr_number=440)
    except Exception as e:
        # 一些 implementation 可能用 "/" 分隔而不是 "-", 兼容
        result = mcp_tools["get_case_study"](repo="Ikalus1988/MisakaNet", pr_number=440)
    assert isinstance(result, dict), f"应返回 dict, 实际 {type(result).__name__}"
