# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-05-28

### Added

- `SKILL.md` — Agent live-thinking compression rules (ZH/EN)
- `scripts/condense.py` — CLI entry (`--quick`, `--stats`, strength presets)
- `scripts/condenser.py` — spaCy full pipeline (semantic + syntactic + dedup)
- `scripts/quick_condense.py` — regex-only mode, zero dependencies
- `scripts/run_tests.py` — bundled test cases
- `examples.md` / `reference.md` — usage docs

### Notes

- Quick mode: ~25–42% compression on verbose reasoning; preserves paths, negations, constraints
- Full mode requires spaCy + `zh_core_web_sm` / `en_core_web_sm`
