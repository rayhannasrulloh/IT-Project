"""
Standalone execution-accuracy evaluation for the NL->SQL agent.

Reuses the app's own AnalystService and gold benchmark suite (the same logic the
Admin -> Benchmarking endpoint uses) but computes a richer metrics report:
  - Overall execution accuracy
  - Per-category accuracy (the closest useful analogue to a per-class F1 table)
  - Latency stats (mean / p50 / p95)
  - Failure-reason breakdown (clarification / guardrail / exec error / mismatch)

Run:  .venv/Scripts/python.exe run_eval.py [--sample N] [--category joins]
"""
import argparse
import asyncio
import statistics
import time
from collections import defaultdict
from itertools import permutations

from app.core.database import AsyncSessionLocal
from app.application.services.analyst_service import AnalystService
from app.application.benchmarks.benchmark_suite import get_suite


def column_subset_match(svc, gold_rows, gen_rows):
    """
    Column-tolerant execution accuracy: the answer is correct if the gold result
    appears as a subset of the generated columns. This credits a semantically
    correct query that returns EXTRA helper columns (e.g. an id alongside a name)
    — which strict full-row comparison wrongly penalizes. Robust to column order,
    aliases (values compared, not names) and row order.
    """
    norm = svc._normalize_cell
    if not gold_rows and not gen_rows:
        return True
    if not gold_rows or not gen_rows:
        return False
    if len(gold_rows) != len(gen_rows):
        return False
    gold_cols = list(gold_rows[0].keys())
    gen_cols = list(gen_rows[0].keys())
    g = len(gold_cols)
    if len(gen_cols) < g:
        return False
    gold_sig = sorted(tuple(norm(r[c]) for c in gold_cols) for r in gold_rows)
    for combo in permutations(gen_cols, g):
        if sorted(tuple(norm(r[c]) for c in combo) for r in gen_rows) == gold_sig:
            return True
    return False


async def evaluate(category=None, sample=None):
    suite = get_suite(category=category, sample=sample)
    results = []

    async with AsyncSessionLocal() as db:
        svc = AnalystService(db)

        async def safe_exec(sql):
            try:
                _, rows, _ = await svc.execute_sql(sql)
                return rows, None
            except Exception as err:
                await db.rollback()
                return None, str(err)

        for i, test in enumerate(suite, 1):
            nl, gold_sql = test["nl_query"], test["gold_sql"]
            t0 = time.time()
            is_ambiguous, clarification, gen_sql, _, _ = await svc.generate_sql(nl)

            strict, adjusted, outcome, err = False, False, "mismatch", None
            if is_ambiguous or not gen_sql:
                outcome, err = "clarification", clarification or "marked ambiguous / no SQL"
            elif not await svc.check_sql_safety(gen_sql):
                outcome, err = "guardrail", "blocked (not read-only)"
            else:
                gold_rows, gold_err = await safe_exec(gold_sql)
                if gold_err:
                    outcome, err = "gold_broken", f"gold failed: {gold_err}"
                else:
                    gen_rows, gen_err = await safe_exec(gen_sql)
                    if gen_err:
                        outcome, err = "exec_error", f"gen failed: {gen_err}"
                    else:
                        strict = svc.compare_result_sets(gold_rows, gen_rows)
                        adjusted = strict or column_subset_match(svc, gold_rows, gen_rows)
                        if strict:
                            outcome = "correct"
                        elif adjusted:
                            outcome = "correct_extra_cols"
                        else:
                            outcome = "mismatch"

            ms = int((time.time() - t0) * 1000)
            results.append({**test, "strict": strict, "adjusted": adjusted,
                            "outcome": outcome, "ms": ms, "err": err})
            flag = "PASS" if strict else ("~ADJ" if adjusted else "FAIL")
            print(f"[{i:2}/{len(suite)}] {flag} ({outcome:18}) {ms:5}ms  {nl[:56]}")

    return results


def report(results):
    n = len(results)
    strict = sum(r["strict"] for r in results)
    adjusted = sum(r["adjusted"] for r in results)
    lat = [r["ms"] for r in results]

    print("\n" + "=" * 66)
    print("  EXECUTION-ACCURACY EVALUATION  —  NL->SQL agent")
    print("=" * 66)
    print(f"  Questions evaluated          : {n}")
    print(f"  STRICT execution accuracy    : {strict}/{n}  {strict/n:.1%}   (exact result set)")
    print(f"  ADJUSTED execution accuracy  : {adjusted}/{n}  {adjusted/n:.1%}   (extra helper cols OK)")
    print("-" * 66)

    print("  Per-category accuracy (strict | adjusted):")
    cats = defaultdict(lambda: [0, 0, 0])
    for r in results:
        cats[r["category"]][0] += r["strict"]
        cats[r["category"]][1] += r["adjusted"]
        cats[r["category"]][2] += 1
    for cat in sorted(cats):
        s, a, t = cats[cat]
        bar = "#" * round(20 * a / t)
        print(f"    {cat:12} {s:2}/{t:<2} {s/t:4.0%} | {a:2}/{t:<2} {a/t:4.0%}  {bar}")
    print("-" * 66)

    print("  Latency (compile+exec):")
    print(f"    mean {statistics.mean(lat):.0f}ms   "
          f"p50 {statistics.median(lat):.0f}ms   "
          f"p95 {sorted(lat)[max(0, round(0.95*len(lat))-1)]:.0f}ms")
    print("-" * 66)

    print("  Failure-reason breakdown:")
    outc = defaultdict(int)
    for r in results:
        outc[r["outcome"]] += 1
    for o in sorted(outc, key=lambda k: -outc[k]):
        print(f"    {o:14} {outc[o]:2}")

    fails = [r for r in results if not r["adjusted"]]
    if fails:
        print("-" * 66)
        print("  Genuinely-wrong cases (fail even under adjusted metric):")
        for r in fails:
            print(f"    [{r['outcome']}] {r['nl_query'][:55]}")
            if r["err"]:
                print(f"        -> {r['err'][:90]}")
    print("=" * 66)


def dump_metrics(results, path):
    """Compute standard eval metrics and write JSON for the report figure.

    Treated as a binary decision per question:
      TP = answered and correct   FP = answered but wrong
      FN = deferred (asked to clarify / guardrail-blocked)
    Precision = answer reliability, Recall = answer coverage.
    """
    import json
    n = len(results)
    tp = sum(r["strict"] for r in results)
    answered = sum(1 for r in results if r["outcome"] in
                   ("correct", "correct_extra_cols", "mismatch", "exec_error"))
    fp = answered - tp
    fn = n - answered
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    cats = defaultdict(lambda: [0, 0])
    for r in results:
        cats[r["category"]][0] += r["strict"]
        cats[r["category"]][1] += 1

    metrics = {
        "n": n,
        "correct": tp,
        "accuracy": tp / n if n else 0.0,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "mean_latency_ms": round(statistics.mean(r["ms"] for r in results)),
        "model": "openai/gpt-oss-120b (Groq)",
        "categories": {c: {"correct": v[0], "total": v[1], "acc": v[0] / v[1]}
                       for c, v in sorted(cats.items())},
    }
    with open(path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\nMetrics written to {path}")
    print(f"  Accuracy {metrics['accuracy']:.1%} | Precision {precision:.1%} | "
          f"Recall {recall:.1%} | F1 {f1:.1%}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=None)
    ap.add_argument("--category", type=str, default=None)
    ap.add_argument("--dump", type=str, default=None, help="write metrics JSON to this path")
    args = ap.parse_args()
    res = asyncio.run(evaluate(category=args.category, sample=args.sample))
    report(res)
    if args.dump:
        dump_metrics(res, args.dump)
