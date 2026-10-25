# graphify knowledge-graph token benchmark

Measurements behind **EP02 — الأدوات الحرة** (https://youtu.be/) — a hands-on test of
[Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) v0.9.92, a tool that turns a
codebase into a queryable knowledge graph. Its README claims **71.5× fewer tokens per query**,
"every edge explained", and "runs entirely locally".

Everything in `results/` was produced by `scripts/benchmark_graphify.py` on one Windows 11
machine, October 2026. The corpus was a **pure-code** project: 38 files (29 code), 19,009
raw tokens. The local AST path only — no LLM key involved.

---

## TL;DR

| claim | advertised | measured on pure code |
| --- | --- | --- |
| token reduction per query | **71.5×** | **8.8×** (average query output 2,162 tokens) |
| "every edge explained" | yes | ✅ **232/232 edges carry a confidence tag** (221 EXTRACTED, 11 INFERRED, 0 AMBIGUOUS) |
| "runs entirely locally" | yes | ✅ all 232 edges carry `_origin=ast` — deterministic, no API key |
| graph as a whole | "smaller context" | ❌ `graph.json` = **28,730 tokens = 151% of the raw source** |
| `--budget` respected | yes | ✅ a 300-token budget returned 1,447 chars |

## The three findings that matter

1. **The 71.5× headline needs a mixed corpus.** Their own README says it was measured over 52
   files of code, papers and **images**. On a plain code repo the honest number is a still-good
   **8.8×** — a third of the headline, not a lie, but not the headline either.
2. **Per-query ≠ wholesale.** The saving only exists when you *ask a narrow question*. Load the
   whole graph and your context gets 51% *worse* than copying the source files verbatim.
3. **The labelling is genuinely honest.** Every edge is tagged, and the 11 INFERRED edges are
   exactly the 11 INDIRECT_CALL edges — the heuristic is declared, not hidden.

## Caveats

- One machine, one version (0.9.92), one pure-code corpus, one day.
- 8.8× is an average over the queries the benchmark ran; query mixes differ.
- The images/docs path of graphify needs a paid Claude pass — not exercised here.
- Percentages will differ on your corpus. The **shape** (SD tagged, origin=ast, graph.json >
  source size, budget respected) should not.

## Reproduce

```
# 1. install graphify  https://github.com/Graphify-Labs/graphify
# 2. run the benchmark against any real project
python scripts/benchmark_graphify.py --project /path/to/your/project
# → results/graphify_benchmark.json
```

## Files

```
scripts/benchmark_graphify.py     the benchmark (nodes, edges, tags, origin fields, token cost)
results/graphify_benchmark.json   raw output: 164 nodes · 232 edges · per-query token counts
```

## Video

**EP02 — حوّلت كود حقيقي لـ knowledge graph.. ورقم الـ71 فيه نص الحقيقة**
English voiceover, Arabic captions on screen. Channel: الأدوات الحرة (@aladawat-alhurra).

---

MIT licensed. Measurements and scripts © الأدوات الحرة.
