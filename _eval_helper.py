#!/usr/bin/env python3
"""Helper: insert evaluations from a JSON file into the database."""
import json
import sys
from models import get_connection, insert_evaluation


def main():
    if len(sys.argv) != 2:
        print("Usage: python _eval_helper.py <evaluations.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        evaluations = json.load(f)

    conn = get_connection()
    success = 0
    for ev in evaluations:
        company_id = ev.pop("company_id")
        try:
            insert_evaluation(conn, company_id, ev)
            success += 1
        except Exception as e:
            print(f"Error inserting company {company_id}: {e}")
    conn.commit()
    conn.close()
    print(f"Inserted {success}/{len(evaluations)} evaluations.")


if __name__ == "__main__":
    main()
