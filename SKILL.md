---
name: think-condenser
description: Compresses AI internal reasoning and long text by removing redundant meta phrases, transitions, and duplicate ideas while preserving keywords, decisions, identifiers, and constraints. Use when the user wants to save tokens, speed up agent runs, condense thinking/reasoning, reduce verbose chain-of-thought, or compress prompts/logs without losing task quality.
---

# Think Condenser

Compress reasoning and text: drop filler, keep signal. Apply in two modes — **live thinking** (default) and **script batch** (existing text).

## Mode 1: Live Thinking (Primary)

Use during internal reasoning. User-facing replies stay full quality; only compress hidden reasoning.

### Keep (never drop)

- Task goal (state once)
- Current hypothesis / decision
- Why that decision (one line max)
- File paths, symbols, API names, error messages, stack traces
- Numbers, negations, conditionals, edge cases
- Blockers and exact next action
- User constraints and rule requirements

### Remove

| Category | Examples (ZH) | Examples (EN) |
|----------|---------------|---------------|
| Meta | 让我思考、我来分析、首先我需要 | Let me think, I will analyze, I need to |
| Transition | 首先、其次、因此、综上所述 | First, Second, Therefore, In conclusion |
| Hedging | 可能、大概、我认为、一般来说 | maybe, probably, I think, generally |
| Rephrase | 换句话说、也就是说、简单来说 | in other words, that is, simply put |
| Duplicate | Same conclusion stated twice | Restating a decision already made |

### Format rules

1. **Telegraphic bullets** — fragments, not polished prose
2. **One idea per line** — merge duplicates before writing
3. **Observe → decide → act** — one pass; no re-exploration loops
4. **Identifiers verbatim** — never abbreviate paths or error text
5. **Stop when decided** — no post-hoc summary of the summary

### Quality guardrails

- If unsure whether something is redundant, **keep it**
- Never compress away: negation (`not`/`不`), branching (`if/else`), numeric thresholds, security/auth details
- Re-read compressed notes: can you still execute the task? If not, restore missing facts
- Target **30–50% token reduction** on reasoning; do not chase ratio at the cost of correctness

### Strength presets

| Preset | When | Behavior |
|--------|------|----------|
| `light` | Debugging, subtle logic | Remove meta/transition only |
| `balanced` | Default | Meta + duplicates + light syntactic trim |
| `aggressive` | Simple lookups, high token pressure | Core facts only; still keep identifiers |

User says "轻度/保守" → `light`. "激进/最大压缩" → `aggressive`. Otherwise → `balanced`.

## Mode 2: Script Batch (Existing Text)

For logs, prompts, transcripts, or pasted reasoning blocks.

### Setup (once per environment)

```bash
pip install -r scripts/requirements.txt
python -m spacy download zh_core_web_sm en_core_web_sm
```

No spaCy? Use quick mode (regex-only, lower quality):

```bash
python scripts/condense.py --quick -i input.txt
```

### CLI usage

```bash
# stdin
echo "让我思考一下…" | python scripts/condense.py

# file → stdout
python scripts/condense.py -i reasoning.txt

# with stats
python scripts/condense.py -i reasoning.txt --stats

# strength: light | balanced | aggressive
python scripts/condense.py -i reasoning.txt -s aggressive
```

### Python API

```python
import sys
sys.path.insert(0, "scripts")
from condenser import BilingualCondenser

c = BilingualCondenser(strength="balanced")
compressed = c.condense(long_text)
compressed, stats = c.condense(long_text, return_stats=True)
```

After script compression, **skim output** for dropped identifiers or negations before using it as agent context.

## Workflow checklist

```
- [ ] Pick strength (default balanced)
- [ ] Strip meta / transition / hedge phrases
- [ ] Deduplicate sentences with same meaning
- [ ] Keep all identifiers, errors, numbers, negations
- [ ] Verify compressed notes still actionable
```

## Examples

See [examples.md](examples.md) for before/after pairs.

## Reference

Pipeline details, blacklist categories, and API options: [reference.md](reference.md)
