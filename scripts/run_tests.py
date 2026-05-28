#!/usr/bin/env python3
"""Run think-condenser test cases."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from quick_condense import quick_condense

CASES = [
    {
        "name": "中文 meta 去除 (examples #3)",
        "input": (
            "让我思考一下这个问题。首先，我需要理解用户的需求。其次，这个问题简单来说就是如何优化代码。"
            "综上所述，我们需要重构这个类。"
        ),
    },
    {
        "name": "英文 debug 推理 (examples #1 风格)",
        "input": (
            "让我先思考一下这个问题。首先，我需要理解用户的报错信息。其次，我认为这个错误可能是因为"
            "空指针导致的。让我再仔细看看 stack trace。综上所述，应该在 UserService.getById 里加空检查。"
        ),
    },
    {
        "name": "英文 refactor (examples #2)",
        "input": (
            "Let me analyze this. First, I need to understand the requirements. I think the user wants to "
            "extract the validation logic. Therefore, we should move it to a separate module. In other words, "
            "create validators.py and import from there."
        ),
    },
    {
        "name": "关键信息保留 (examples #4)",
        "input": (
            "Error: HTTP 403 on POST /api/admin/users — missing scope \"users:write\"\n"
            "Constraint: do NOT use --no-verify on commit\n"
            "Branch: if env=prod → require MFA; else skip\n"
            "File: src/auth/middleware.ts:87"
        ),
    },
    {
        "name": "重复句去重 (examples #5)",
        "input": (
            "The cache key must include userId. We need userId in the cache key.\n"
            "TTL should be 300 seconds. Cache TTL: 300s."
        ),
    },
    {
        "name": "双语混合",
        "input": (
            "让我思考一下这个问题。首先，我需要理解用户的需求。其次，这个问题简单来说就是如何优化代码。"
            "综上所述，我们需要重构这个类。\n"
            "Let me analyze this. First, I need to understand the requirements. Second, this problem is "
            "simply about code optimization. Therefore, we need to refactor this class."
        ),
    },
]


def run_quick():
    print("=" * 60)
    print("Quick 模式测试 (无 spaCy 依赖)")
    print("=" * 60)
    for case in CASES:
        inp = case["input"]
        out = quick_condense(inp, strength="balanced")
        ratio = round(1 - len(out) / len(inp), 2) if inp else 0
        print(f"\n【{case['name']}】")
        print(f"  原文 ({len(inp)} 字): {inp[:80]}{'...' if len(inp) > 80 else ''}")
        print(f"  压缩 ({len(out)} 字, -{ratio*100:.0f}%): {out[:120]}{'...' if len(out) > 120 else ''}")


def run_full():
    try:
        from condenser import BilingualCondenser
    except ImportError:
        print("\n[跳过] spaCy 未安装，无法运行完整模式")
        return

    try:
        condenser = BilingualCondenser(strength="balanced", lazy_load=True)
        _ = condenser.nlp_zh  # trigger load
    except OSError as exc:
        print(f"\n[跳过] spaCy 语言模型未安装: {exc}")
        return

    print("\n" + "=" * 60)
    print("Full 模式测试 (spaCy NLP)")
    print("=" * 60)
    for case in CASES[:3]:
        inp = case["input"]
        out, stats = condenser.condense(inp, return_stats=True)
        print(f"\n【{case['name']}】")
        print(f"  原文 ({stats['original_length']} 字)")
        print(f"  压缩 ({stats['compressed_length']} 字, -{stats['compression_ratio']*100:.0f}%)")
        print(f"  结果: {out[:120]}{'...' if len(out) > 120 else ''}")


if __name__ == "__main__":
    run_quick()
    run_full()
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
