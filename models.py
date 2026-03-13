import sqlite3
import os
from config import DB_PATH


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    conn = get_connection()
    with open(schema_path) as f:
        conn.executescript(f.read())
    conn.close()


def get_unevaluated_companies(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("""
        SELECT c.id, c.name, c.one_liner, c.long_description, c.subindustry,
               c.status, c.stage, c.team_size,
               GROUP_CONCAT(t.name, ', ') AS tags
        FROM companies c
        LEFT JOIN company_tags ct ON c.id = ct.company_id
        LEFT JOIN tags t ON ct.tag_id = t.id
        LEFT JOIN evaluations e ON c.id = e.company_id
        WHERE e.company_id IS NULL
        GROUP BY c.id
    """).fetchall()
    return [dict(r) for r in rows]


def insert_evaluation(conn: sqlite3.Connection, company_id: int, data: dict):
    conn.execute("""
        INSERT OR REPLACE INTO evaluations
        (company_id, urgency, market_size, pricing_potential, acquisition_cost,
         delivery_cost, uniqueness, speed_to_market, upfront_investment,
         upsell_potential, evergreen_potential, replicability, niche_category, reasoning)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        company_id,
        data["urgency"], data["market_size"], data["pricing_potential"],
        data["acquisition_cost"], data["delivery_cost"], data["uniqueness"],
        data["speed_to_market"], data["upfront_investment"],
        data["upsell_potential"], data["evergreen_potential"],
        data["replicability"], data["niche_category"], data["reasoning"],
    ))
