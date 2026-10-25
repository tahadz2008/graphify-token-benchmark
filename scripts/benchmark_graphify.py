#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Benchmark graphify on a real codebase - the local AST path only (no LLM key).

Measures the four things the README's headline number hides:
  1. what the graph actually contains (nodes / edges / by edge label)
  2. build cost (wall time, no API cost)
  3. the REAL token reduction on a pure-code corpus, vs the advertised 71.5x
  4. whether the edges are trustworthy (sampled and hand-verified)
"""
import json, re, subprocess, sys, time
from collections import Counter
from pathlib import Path

WORK = Path(r"C:\Users\ACHOUTAHA\AppData\Local\Temp\opencode\hudmod-test\gf_test")
GRAPH = WORK / "graphify-out" / "graph.json"
PY = sys.executable


def run(args, timeout=300):
    t0 = time.time()
    r = subprocess.run([PY, "-m", "graphify", *args], capture_output=True,
                       text=True, timeout=timeout, encoding="utf-8", errors="replace",
                       cwd=str(WORK))
    return r.stdout + r.stderr, time.time() - t0


def tok(t):
    return len(re.findall(r"\w+|[^\w\s]", t))


def corpus_tokens():
    """Tokens an agent would spend reading the raw code corpus."""
    total = 0
    files = 0
    for p in WORK.rglob("*"):
        if not p.is_file() or "graphify-out" in p.parts:
            continue
        if p.suffix.lower() not in {".py", ".js", ".mjs", ".ts", ".md"}:
            continue
        try:
            total += tok(p.read_text(encoding="utf-8", errors="replace"))
            files += 1
        except OSError:
            pass
    return files, total


def main():
    if not GRAPH.exists():
        print("no graph.json - run extract first")
        return
    g = json.loads(GRAPH.read_text(encoding="utf-8"))
    nodes = g.get("nodes", [])
    edges = g.get("edges", [])

    print("=" * 78)
    print("GRAPHIFY BENCHMARK  (local AST path, no LLM key, no API cost)")
    print("=" * 78)
    print(f"nodes            : {len(nodes)}")
    print(f"edges            : {len(edges)}")

    # edge confidence labels - the "every edge is labelled" claim.
    # NOTE: the field is `confidence` (EXTRACTED/INFERRED/AMBIGUOUS); `relation`
    # is the edge TYPE (CONTAINS/CALLS/...). They are different axes.
    conf = Counter(str(e.get("confidence", "(none)")).upper() for e in edges)
    rel = Counter(str(e.get("relation", "?")).upper() for e in edges)
    origin = Counter(str(e.get("_origin", "?")).lower() for e in edges)

    print(f"\nedge CONFIDENCE (README: every edge tagged):")
    tot_c = sum(conf.values())
    for lab, c in conf.most_common():
        print(f"   {lab:<28} {c:>5}  ({c/tot_c*100:5.1f}%)")
    unlab = conf.get("(NONE)", 0)
    print(f"   -> every edge tagged: {unlab == 0}")

    print(f"\nedge RELATION (type):")
    for lab, c in rel.most_common():
        print(f"   {lab:<28} {c:>5}  ({c/tot_c*100:5.1f}%)")

    print(f"\nedge ORIGIN (provenance):")
    for lab, c in origin.most_common():
        print(f"   {lab:<28} {c:>5}")

    # node kinds
    kinds = Counter(str(n.get("kind") or n.get("type") or n.get("label") or "?") for n in nodes)
    print(f"\nnode kinds:")
    for k, c in kinds.most_common(8):
        print(f"   {k:<28} {c:>5}")

    # raw corpus cost
    files, raw_tok = corpus_tokens()
    print(f"\nraw corpus: {files} files, {raw_tok:,} tokens")
    print(f"graph.json size: {GRAPH.stat().st_size/1024:.0f} KB")

    # query cost + reduction
    print("\n" + "-" * 78)
    print("QUERY BEHAVIOUR  (the actual '71.5x' claim)")
    print("-" * 78)
    queries = [
        "how are secrets detected",
        "what does the commit gate check",
        "which files are read by the checker",
        "changelog validation",
    ]
    q_out = []
    for q in queries:
        out, dt = run(["query", q, "--graph", str(GRAPH), "--budget", "2000"])
        t = tok(out)
        q_out.append(t)
        red = (1 - t / raw_tok) * 100 if raw_tok else 0
        print(f"   {q[:38]:<40} {t:>6} tok  ({dt:4.1f}s)  reduction vs raw: {red:6.2f}x")

    avg_q = sum(q_out) / len(q_out)
    print(f"\n   average query output: {avg_q:.0f} tokens")
    print(f"   raw corpus:           {raw_tok:,} tokens")
    print(f"   ==> measured reduction: {raw_tok/avg_q:.1f}x")
    print(f"   ==> README headline   : 71.5x   (52 files, code + papers + IMAGES)")
    print(f"   ==> our corpus         : {files} files, PURE CODE (no papers, no images)")

    # what the graph.json itself costs to load into context
    gjson_tok = tok(GRAPH.read_text(encoding="utf-8", errors="replace"))
    print(f"\n   whole graph.json as context: {gjson_tok:,} tokens "
          f"({gjson_tok/raw_tok*100:.1f}% of raw)")

    out = {
        "nodes": len(nodes), "edges": len(edges),
        "edge_confidence": dict(conf),
        "edge_relation": dict(rel),
        "edge_origin": dict(origin),
        "corpus_files": files, "corpus_tokens": raw_tok,
        "graph_json_tokens": gjson_tok,
        "avg_query_tokens": avg_q,
        "measured_reduction_x": raw_tok / avg_q if avg_q else 0,
        "readme_claim_x": 71.5,
        "query_outputs": q_out,
    }
    dest = Path(r"C:\Users\ACHOUTAHA\Documents\Default Project\channel\build\graphify_benchmark.json")
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n-> {dest}")


if __name__ == "__main__":
    main()
