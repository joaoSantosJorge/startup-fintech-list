#!/usr/bin/env python3
"""Run analytics queries and print reports."""

from tabulate import tabulate
from models import get_connection

DIMENSIONS = [
    "urgency", "market_size", "pricing_potential", "acquisition_cost",
    "delivery_cost", "uniqueness", "speed_to_market", "upfront_investment",
    "upsell_potential", "evergreen_potential",
]


def report_top_companies(conn, n=20):
    rows = conn.execute("""
        SELECT c.name, c.one_liner, e.total_score, e.replicability, e.niche_category
        FROM evaluations e JOIN companies c ON e.company_id = c.id
        ORDER BY e.total_score DESC
        LIMIT ?
    """, (n,)).fetchall()
    print(f"\n{'='*80}")
    print(f"  TOP {n} COMPANIES BY TOTAL SCORE")
    print(f"{'='*80}")
    table = [[r["name"], r["total_score"], r["replicability"], r["niche_category"],
              (r["one_liner"] or "")[:60]] for r in rows]
    print(tabulate(table, headers=["Name", "Score", "Replic.", "Niche", "One-liner"], tablefmt="simple"))


def report_score_distribution(conn):
    buckets = conn.execute("""
        SELECT
            CASE
                WHEN total_score >= 70 THEN 'Excellent (70+)'
                WHEN total_score >= 55 THEN 'Strong (55-69)'
                WHEN total_score >= 40 THEN 'Average (40-54)'
                ELSE 'Weak (<40)'
            END AS bucket,
            COUNT(*) AS count
        FROM evaluations
        GROUP BY bucket
        ORDER BY MIN(total_score) DESC
    """).fetchall()
    print(f"\n{'='*80}")
    print("  SCORE DISTRIBUTION")
    print(f"{'='*80}")
    table = [[r["bucket"], r["count"]] for r in buckets]
    print(tabulate(table, headers=["Bucket", "Count"], tablefmt="simple"))


def report_best_niches(conn):
    rows = conn.execute("""
        SELECT niche_category,
               COUNT(*) AS count,
               ROUND(AVG(total_score), 1) AS avg_score,
               MAX(total_score) AS max_score,
               ROUND(AVG(replicability), 1) AS avg_replic
        FROM evaluations
        GROUP BY niche_category
        ORDER BY avg_score DESC
    """).fetchall()
    print(f"\n{'='*80}")
    print("  BEST NICHES BY AVERAGE SCORE")
    print(f"{'='*80}")
    table = [[r["niche_category"], r["count"], r["avg_score"], r["max_score"], r["avg_replic"]]
             for r in rows]
    print(tabulate(table, headers=["Niche", "Count", "Avg Score", "Max Score", "Avg Replic."], tablefmt="simple"))


def report_most_replicable(conn, min_replicability=7):
    rows = conn.execute("""
        SELECT c.name, c.one_liner, e.total_score, e.replicability, e.niche_category
        FROM evaluations e JOIN companies c ON e.company_id = c.id
        WHERE e.replicability >= ?
        ORDER BY e.total_score DESC
        LIMIT 20
    """, (min_replicability,)).fetchall()
    print(f"\n{'='*80}")
    print(f"  MOST REPLICABLE HIGH-SCORING IDEAS (replicability >= {min_replicability})")
    print(f"{'='*80}")
    table = [[r["name"], r["total_score"], r["replicability"], r["niche_category"],
              (r["one_liner"] or "")[:60]] for r in rows]
    print(tabulate(table, headers=["Name", "Score", "Replic.", "Niche", "One-liner"], tablefmt="simple"))


def report_dimension_averages(conn):
    selects = ", ".join(f"ROUND(AVG({d}), 1) AS {d}" for d in DIMENSIONS)
    row = conn.execute(f"SELECT {selects} FROM evaluations").fetchone()
    print(f"\n{'='*80}")
    print("  AVERAGE SCORE PER DIMENSION")
    print(f"{'='*80}")
    table = [[d.replace("_", " ").title(), row[d]] for d in DIMENSIONS]
    print(tabulate(table, headers=["Dimension", "Avg Score"], tablefmt="simple"))


def report_niche_rankings(conn):
    niches = conn.execute("""
        SELECT DISTINCT niche_category FROM evaluations ORDER BY niche_category
    """).fetchall()
    print(f"\n{'='*80}")
    print("  TOP 5 COMPANIES PER NICHE")
    print(f"{'='*80}")
    for niche_row in niches:
        niche = niche_row["niche_category"]
        rows = conn.execute("""
            SELECT c.name, e.total_score, e.replicability
            FROM evaluations e JOIN companies c ON e.company_id = c.id
            WHERE e.niche_category = ?
            ORDER BY e.total_score DESC LIMIT 5
        """, (niche,)).fetchall()
        print(f"\n  >> {niche}")
        table = [[r["name"], r["total_score"], r["replicability"]] for r in rows]
        print(tabulate(table, headers=["Name", "Score", "Replic."], tablefmt="simple"))


def report_active_vs_inactive(conn):
    rows = conn.execute("""
        SELECT c.status,
               COUNT(*) AS count,
               ROUND(AVG(e.total_score), 1) AS avg_score
        FROM evaluations e JOIN companies c ON e.company_id = c.id
        GROUP BY c.status
        ORDER BY avg_score DESC
    """).fetchall()
    print(f"\n{'='*80}")
    print("  ACTIVE vs INACTIVE SCORE COMPARISON")
    print(f"{'='*80}")
    table = [[r["status"], r["count"], r["avg_score"]] for r in rows]
    print(tabulate(table, headers=["Status", "Count", "Avg Score"], tablefmt="simple"))


def main():
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM evaluations").fetchone()[0]
    if total == 0:
        print("No evaluations found. Run 02_evaluate.py first.")
        conn.close()
        return

    print(f"Analyzing {total} evaluated companies...\n")

    report_top_companies(conn)
    report_score_distribution(conn)
    report_best_niches(conn)
    report_most_replicable(conn)
    report_dimension_averages(conn)
    report_niche_rankings(conn)
    report_active_vs_inactive(conn)

    conn.close()
    print(f"\n{'='*80}")
    print("  Analysis complete!")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
