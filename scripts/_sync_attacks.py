#!/usr/bin/env python3
"""Deduplicate attacks.json and push all to Supabase in small batches."""

import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("sync_attacks")

import db as supabase_db

DATA_DIR = Path(__file__).parent.parent / "data"


def main():
    # Load and deduplicate
    attacks = json.loads((DATA_DIR / "attacks.json").read_text())
    print(f"Loaded {len(attacks)} attacks from local file")

    seen = set()
    deduped = []
    for a in attacks:
        if a["id"] not in seen:
            seen.add(a["id"])
            deduped.append(a)

    print(f"After dedup: {len(deduped)} unique attacks")

    # Save deduped back to file
    (DATA_DIR / "attacks.json").write_text(json.dumps(deduped, indent=2, ensure_ascii=False))
    print("Saved deduplicated attacks.json")

    # Push to Supabase in batches of 100 (small enough to avoid dupe issues)
    client = supabase_db.get_client()
    if client is None:
        print("ERROR: Supabase not configured")
        return

    total = 0
    batch_size = 100
    for i in range(0, len(deduped), batch_size):
        batch = deduped[i : i + batch_size]
        rows = [supabase_db._attack_to_row(a) for a in batch]
        try:
            client.table("attacks").upsert(rows, on_conflict="id").execute()
            total += len(rows)
            print(f"  Batch {i // batch_size + 1}: upserted {len(rows)} ({total}/{len(deduped)})")
        except Exception as e:
            print(f"  Batch {i // batch_size + 1}: FAILED - {e}")

    print(f"\nDone: {total}/{len(deduped)} attacks synced to Supabase")

    # Verify
    resp = client.table("attacks").select("id", count="exact").execute()
    count = resp.count if resp.count is not None else len(resp.data or [])
    print(f"Supabase attacks count: {count}")


if __name__ == "__main__":
    main()
