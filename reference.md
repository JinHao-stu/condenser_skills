# Think Condenser Reference

## Processing pipeline (script mode)

1. **Preprocess** — mask URLs/emails as `[URL]` / `[EMAIL]`
2. **Semantic filter** — regex removal of meta, transition, blacklist phrases
3. **Syntactic compress** — spaCy dependency parse; keep core deps (nsubj, ROOT, dobj, …) + nouns/verbs/adj
4. **Statistical filter** — drop chars/words repeating above frequency threshold
5. **Duplicate filter** — Jaccard + sentence similarity; remove near-duplicate sentences
6. **Post-process** — normalize punctuation and whitespace

## Blacklist categories

| Category | Purpose |
|----------|---------|
| `meta` | Agent self-narration |
| `transition` | Sequential filler |
| `hesitation` | Low-information hedging |
| `explanation` | Rephrasing connectors |

Custom markers: pass `custom_explanation_markers=["换言之"]` to `BilingualCondenser()`.

## API options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `strength` | `"balanced"` | `light` / `balanced` / `aggressive` |
| `similarity_threshold` | `0.85` | Duplicate sentence cutoff |
| `enable_duplicate_filter` | `True` | Toggle dedup pass |
| `lazy_load` | `True` | Defer spaCy model load |
| `return_stats` | `False` | Return `{original_length, compressed_length, compression_ratio}` |

## When to prefer live vs script

| Scenario | Mode |
|----------|------|
| Agent solving a task now | Live thinking |
| Compressing chat export / log file | Script |
| spaCy not installed | `--quick` or live thinking |
| Must preserve exact wording (legal/code) | Live thinking + manual review |

## Token savings (typical)

| Content type | Balanced reduction |
|--------------|-------------------|
| Verbose agent reasoning | 35–55% |
| Prompt with filler | 25–40% |
| Already terse notes | 5–15% |

Higher reduction ≠ better. Stop if actionable details disappear.
