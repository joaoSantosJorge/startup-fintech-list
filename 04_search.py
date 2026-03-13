#!/usr/bin/env python3
"""CLI search by niche, keyword, score, or replicability."""

import argparse
from tabulate import tabulate
from models import get_connection


def search(args):
    conn = get_connection()
    conditions = []
    params = []

    if args.niche:
        conditions.append("e.niche_category LIKE ?")
        params.append(f"%{args.niche}%")

    if args.keyword:
        conditions.append("(c.name LIKE ? OR c.one_liner LIKE ? OR c.long_description LIKE ?)")
        params.extend([f"%{args.keyword}%"] * 3)

    if args.min_score:
        conditions.append("e.total_score >= ?")
        params.append(args.min_score)

    if args.replicable:
        conditions.append("e.replicability >= ?")
        params.append(args.replicable)

    if args.batch:
        conditions.append("c.batch = ?")
        params.append(args.batch)

    if args.status:
        conditions.append("c.status = ?")
        params.append(args.status)

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    limit = args.top or 20

    query = f"""
        SELECT c.name, c.one_liner, c.website, c.batch, c.status,
               e.total_score, e.replicability, e.niche_category, e.reasoning
        FROM evaluations e
        JOIN companies c ON e.company_id = c.id
        {where}
        ORDER BY e.total_score DESC
        LIMIT ?
    """
    params.append(limit)
    rows = conn.execute(query, params).fetchall()

    if not rows:
        print("No results found.")
        conn.close()
        return

    print(f"\nFound {len(rows)} result(s):\n")

    if args.verbose:
        for r in rows:
            print(f"{'─'*70}")
            print(f"  {r['name']} (Score: {r['total_score']}, Replicability: {r['replicability']})")
            print(f"  Niche: {r['niche_category']} | Batch: {r['batch']} | Status: {r['status']}")
            print(f"  {r['one_liner']}")
            print(f"  Website: {r['website']}")
            print(f"  Reasoning: {r['reasoning']}")
        print(f"{'─'*70}")
    else:
        table = [
            [r["name"], r["total_score"], r["replicability"],
             r["niche_category"], r["batch"],
             (r["one_liner"] or "")[:55]]
            for r in rows
        ]
        print(tabulate(table,
                        headers=["Name", "Score", "Replic.", "Niche", "Batch", "One-liner"],
                        tablefmt="simple"))

    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Search YC fintech companies by various criteria")
    parser.add_argument("--niche", help="Filter by niche category (e.g., Payments, Lending)")
    parser.add_argument("--keyword", help="Search name, one-liner, and description")
    parser.add_argument("--min-score", type=int, help="Minimum total score")
    parser.add_argument("--replicable", type=int, help="Minimum replicability score")
    parser.add_argument("--batch", help="Filter by YC batch (e.g., W21, S22)")
    parser.add_argument("--status", help="Filter by status (e.g., Active, Inactive)")
    parser.add_argument("--top", type=int, help="Number of results to show (default: 20)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed output with reasoning")
    args = parser.parse_args()

    search(args)


if __name__ == "__main__":
    main()
