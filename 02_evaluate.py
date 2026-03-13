#!/usr/bin/env python3
"""Score companies via Claude Batch API using the 10 Ways framework."""

import json
import time
import sys
import anthropic
from config import CLAUDE_MODEL, CLAUDE_MAX_TOKENS
from models import get_connection, get_unevaluated_companies, insert_evaluation
from prompts import EVALUATION_SYSTEM_PROMPT, build_evaluation_prompt


SCORE_FIELDS = [
    "urgency", "market_size", "pricing_potential", "acquisition_cost",
    "delivery_cost", "uniqueness", "speed_to_market", "upfront_investment",
    "upsell_potential", "evergreen_potential", "replicability",
]


def validate_evaluation(data: dict) -> bool:
    for field in SCORE_FIELDS:
        val = data.get(field)
        if not isinstance(val, int) or not 1 <= val <= 10:
            return False
    if "niche_category" not in data or "reasoning" not in data:
        return False
    return True


def parse_response_text(text: str) -> dict | None:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    try:
        data = json.loads(text)
        if validate_evaluation(data):
            return data
    except json.JSONDecodeError:
        pass
    return None


def build_batch_requests(companies: list[dict]) -> list[dict]:
    requests = []
    for c in companies:
        requests.append({
            "custom_id": str(c["id"]),
            "params": {
                "model": CLAUDE_MODEL,
                "max_tokens": CLAUDE_MAX_TOKENS,
                "messages": [
                    {"role": "user", "content": build_evaluation_prompt(c)},
                ],
                "system": EVALUATION_SYSTEM_PROMPT,
            },
        })
    return requests


def run_batch(client: anthropic.Anthropic, companies: list[dict]) -> str:
    requests = build_batch_requests(companies)
    print(f"Submitting batch of {len(requests)} requests...")
    batch = client.messages.batches.create(requests=requests)
    print(f"Batch created: {batch.id}")
    return batch.id


def poll_batch(client: anthropic.Anthropic, batch_id: str) -> bool:
    while True:
        batch = client.messages.batches.retrieve(batch_id)
        status = batch.processing_status
        counts = batch.request_counts
        print(f"  Status: {status} | succeeded={counts.succeeded} "
              f"errored={counts.errored} processing={counts.processing}")
        if status == "ended":
            return True
        time.sleep(15)


def process_batch_results(client: anthropic.Anthropic, batch_id: str, conn):
    success = 0
    failed = 0
    for result in client.messages.batches.results(batch_id):
        company_id = int(result.custom_id)
        if result.result.type == "succeeded":
            text = result.result.message.content[0].text
            data = parse_response_text(text)
            if data:
                insert_evaluation(conn, company_id, data)
                success += 1
            else:
                print(f"  Failed to parse response for company {company_id}")
                failed += 1
        else:
            print(f"  Request failed for company {company_id}: {result.result.type}")
            failed += 1
    conn.commit()
    print(f"Batch results: {success} succeeded, {failed} failed")
    return success, failed


def run_individual_fallback(client: anthropic.Anthropic, companies: list[dict], conn):
    """Fallback: evaluate one by one if batch API is unavailable."""
    success = 0
    failed = 0
    total = len(companies)
    for i, c in enumerate(companies, 1):
        print(f"  [{i}/{total}] Evaluating {c['name']}...", end=" ")
        try:
            resp = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=CLAUDE_MAX_TOKENS,
                system=EVALUATION_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": build_evaluation_prompt(c)}],
            )
            data = parse_response_text(resp.content[0].text)
            if data:
                insert_evaluation(conn, c["id"], data)
                success += 1
                print("OK")
            else:
                print("PARSE ERROR")
                failed += 1
        except Exception as e:
            print(f"ERROR: {e}")
            failed += 1

        if i % 50 == 0:
            conn.commit()
            print(f"  Committed {i}/{total}")

    conn.commit()
    print(f"Individual results: {success} succeeded, {failed} failed")
    return success, failed


def main():
    conn = get_connection()
    companies = get_unevaluated_companies(conn)

    if not companies:
        print("All companies already evaluated!")
        conn.close()
        return

    print(f"Found {len(companies)} unevaluated companies.")
    client = anthropic.Anthropic()

    use_batch = "--no-batch" not in sys.argv

    if use_batch:
        try:
            batch_id = run_batch(client, companies)
            print("Polling for batch completion...")
            poll_batch(client, batch_id)
            process_batch_results(client, batch_id, conn)
        except Exception as e:
            print(f"Batch API failed ({e}), falling back to individual calls...")
            # Re-fetch unevaluated in case some were done
            companies = get_unevaluated_companies(conn)
            if companies:
                run_individual_fallback(client, companies, conn)
    else:
        print("Using individual API calls (--no-batch mode)...")
        run_individual_fallback(client, companies, conn)

    total_evaluated = conn.execute("SELECT COUNT(*) FROM evaluations").fetchone()[0]
    print(f"\nTotal evaluations in DB: {total_evaluated}")
    conn.close()


if __name__ == "__main__":
    main()
