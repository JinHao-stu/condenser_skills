#!/usr/bin/env python3
"""CLI for think-condenser — compress verbose reasoning/text."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from quick_condense import quick_condense  # noqa: E402


def read_input(path: str | None) -> str:
    if path and path != "-":
        return Path(path).read_text(encoding="utf-8")
    return sys.stdin.read()


def main() -> int:
    parser = argparse.ArgumentParser(description="Compress verbose AI reasoning / filler text")
    parser.add_argument("-i", "--input", help="Input file path (default: stdin)")
    parser.add_argument("-s", "--strength", choices=["light", "balanced", "aggressive"], default="balanced")
    parser.add_argument("--stats", action="store_true", help="Print compression stats to stderr")
    parser.add_argument("--quick", action="store_true", help="Regex-only mode (no spaCy)")
    args = parser.parse_args()

    text = read_input(args.input)
    if not text.strip():
        print("", end="")
        return 0

    if args.quick:
        result = quick_condense(text, strength=args.strength)
        stats = {
            "original_length": len(text),
            "compressed_length": len(result),
            "compression_ratio": round(1 - len(result) / len(text), 2) if text else 0,
            "mode": "quick",
        }
    else:
        try:
            from condenser import BilingualCondenser  # noqa: E402

            condenser = BilingualCondenser(strength=args.strength)
            if args.stats:
                result, stats = condenser.condense(text, return_stats=True)
                stats["mode"] = "full"
            else:
                result = condenser.condense(text)
                stats = None
        except OSError as exc:
            print(f"spaCy models missing ({exc}). Use --quick or install models.", file=sys.stderr)
            return 1

    print(result, end="")
    if args.stats and stats:
        print(f"\n{stats}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
