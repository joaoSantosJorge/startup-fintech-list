#!/usr/bin/env python3
"""Fetch YC fintech companies from the API and populate SQLite."""

import requests
from config import API_URL
from models import get_connection, init_db


def fetch_companies() -> list[dict]:
    print(f"Fetching companies from {API_URL} ...")
    resp = requests.get(API_URL, timeout=30)
    resp.raise_for_status()
    companies = resp.json()
    print(f"Fetched {len(companies)} companies.")
    return companies


def insert_companies(conn, companies: list[dict]):
    inserted = 0
    for c in companies:
        cid = c.get("id")
        if cid is None:
            continue

        conn.execute("""
            INSERT OR IGNORE INTO companies
            (id, name, slug, website, all_locations, long_description, one_liner,
             team_size, industry, subindustry, batch, status, stage,
             top_company, is_hiring, launched_at, yc_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            cid,
            c.get("name"),
            c.get("slug"),
            c.get("website"),
            c.get("all_locations"),
            c.get("long_description"),
            c.get("one_liner"),
            c.get("team_size"),
            c.get("industry"),
            c.get("subindustry"),
            c.get("batch"),
            c.get("status"),
            c.get("stage"),
            1 if c.get("top_company") else 0,
            1 if c.get("is_hiring") else 0,
            c.get("launched_at"),
            f"https://www.ycombinator.com/companies/{c.get('slug', '')}",
        ))
        inserted += 1

        # Tags
        for tag in c.get("tags", []) or []:
            conn.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
            tag_id = conn.execute("SELECT id FROM tags WHERE name = ?", (tag,)).fetchone()[0]
            conn.execute("INSERT OR IGNORE INTO company_tags (company_id, tag_id) VALUES (?, ?)", (cid, tag_id))

        # Industries
        for ind in c.get("industries", []) or []:
            conn.execute("INSERT OR IGNORE INTO company_industries (company_id, industry_name) VALUES (?, ?)", (cid, ind))

        # Regions
        for reg in c.get("regions", []) or []:
            conn.execute("INSERT OR IGNORE INTO company_regions (company_id, region_name) VALUES (?, ?)", (cid, reg))

    conn.commit()
    return inserted


def main():
    init_db()
    companies = fetch_companies()
    conn = get_connection()
    try:
        count = insert_companies(conn, companies)
        print(f"Inserted {count} companies into the database.")

        total = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
        tag_count = conn.execute("SELECT COUNT(*) FROM tags").fetchone()[0]
        print(f"Total companies in DB: {total}")
        print(f"Total unique tags: {tag_count}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
