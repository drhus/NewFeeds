#!/usr/bin/env python3
"""
Check local JSON data vs Supabase and sync any missing data.
"""

import json
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("check_sync")

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
FEEDS_DIR = DATA_DIR / "feeds"

import db as supabase_db


def count_local():
    """Count all local JSON data."""
    print("\n" + "=" * 60)
    print("LOCAL JSON DATA")
    print("=" * 60)

    # Articles per region
    regions = {}
    for f in sorted(FEEDS_DIR.glob("*.json")):
        region = f.stem
        articles = json.loads(f.read_text())
        regions[region] = len(articles)

    total_local = 0
    for r, c in regions.items():
        print(f"  articles/{r}: {c}")
        total_local += c
    print(f"  TOTAL articles: {total_local}")

    # Attacks
    attacks = json.loads((DATA_DIR / "attacks.json").read_text())
    print(f"  attacks: {len(attacks)}")

    # Threat level
    threat = json.loads((DATA_DIR / "threat_level.json").read_text())
    print(f"  threat_level: present (level={threat.get('current', {}).get('label', '?')})")

    # Executive summary
    summary = json.loads((DATA_DIR / "executive_summary.json").read_text())
    print(f"  executive_summary: present (generated_at={summary.get('generated_at', '?')})")

    return regions, attacks, threat, summary


def count_supabase():
    """Count all Supabase data."""
    print("\n" + "=" * 60)
    print("SUPABASE DATA")
    print("=" * 60)

    client = supabase_db.get_client()
    if client is None:
        print("  ERROR: Supabase not configured")
        return {}

    # Articles per region
    regions_sb = {}
    try:
        resp = client.table("articles").select("region", count="exact").execute()
        # Count by region using a different approach
        for region in ["china", "gulf", "iran", "israel", "middle_east", "proxies", "russia", "south_asia", "turkey", "western"]:
            resp = client.table("articles").select("id", count="exact").eq("region", region).execute()
            count = resp.count if resp.count is not None else len(resp.data or [])
            regions_sb[region] = count
            print(f"  articles/{region}: {count}")
    except Exception as e:
        print(f"  ERROR counting articles: {e}")

    total_sb = sum(regions_sb.values())
    print(f"  TOTAL articles: {total_sb}")

    # Attacks
    try:
        resp = client.table("attacks").select("id", count="exact").execute()
        attacks_count = resp.count if resp.count is not None else len(resp.data or [])
        print(f"  attacks: {attacks_count}")
    except Exception as e:
        print(f"  ERROR counting attacks: {e}")
        attacks_count = 0

    # Threat level
    try:
        resp = client.table("threat_level").select("*").eq("id", "current").single().execute()
        row = resp.data
        if row:
            cd = row.get("current_data", {})
            if isinstance(cd, str):
                cd = json.loads(cd)
            label = cd.get("label", "?") if cd else "empty"
            print(f"  threat_level: present (level={label})")
        else:
            print(f"  threat_level: MISSING")
    except Exception as e:
        print(f"  threat_level: ERROR - {e}")

    # Executive summary
    try:
        resp = client.table("executive_summary").select("*").eq("id", "current").single().execute()
        row = resp.data
        if row:
            data = row.get("data", {})
            if isinstance(data, str):
                data = json.loads(data)
            gen_at = data.get("generated_at", row.get("generated_at", "?"))
            print(f"  executive_summary: present (generated_at={gen_at})")
        else:
            print(f"  executive_summary: MISSING")
    except Exception as e:
        print(f"  executive_summary: ERROR - {e}")

    # Operational briefing
    try:
        resp = client.table("operational_briefing").select("*").eq("id", "current").single().execute()
        row = resp.data
        if row:
            data = row.get("data", {})
            if isinstance(data, str):
                data = json.loads(data)
            gen_at = data.get("generated_at", row.get("generated_at", "?"))
            is_empty = not data or data == {}
            if is_empty:
                print(f"  operational_briefing: EMPTY (no data yet)")
            else:
                print(f"  operational_briefing: present (generated_at={gen_at})")
        else:
            print(f"  operational_briefing: MISSING")
    except Exception as e:
        print(f"  operational_briefing: ERROR - {e}")

    return regions_sb, attacks_count


def sync_data(local_regions, local_attacks, local_threat, local_summary, sb_regions, sb_attacks_count):
    """Push missing data from local JSON to Supabase."""
    print("\n" + "=" * 60)
    print("SYNCING MISSING DATA TO SUPABASE")
    print("=" * 60)

    synced = False

    # Sync articles per region
    for region, local_count in local_regions.items():
        sb_count = sb_regions.get(region, 0)
        if sb_count < local_count:
            print(f"  {region}: Supabase has {sb_count}, local has {local_count} — syncing...")
            articles = json.loads((FEEDS_DIR / f"{region}.json").read_text())
            count = supabase_db.upsert_articles(region, articles)
            print(f"    -> upserted {count} articles")
            synced = True
        else:
            print(f"  {region}: OK ({sb_count} >= {local_count})")

    # Sync attacks
    if sb_attacks_count < len(local_attacks):
        print(f"  attacks: Supabase has {sb_attacks_count}, local has {len(local_attacks)} — syncing...")
        count = supabase_db.upsert_attacks(local_attacks)
        print(f"    -> upserted {count} attacks")
        synced = True
    else:
        print(f"  attacks: OK ({sb_attacks_count} >= {len(local_attacks)})")

    # Sync threat level
    print(f"  threat_level: upserting latest local data...")
    supabase_db.upsert_threat_level(local_threat)
    synced = True

    # Sync executive summary
    print(f"  executive_summary: upserting latest local data...")
    supabase_db.upsert_executive_summary(local_summary)
    synced = True

    if synced:
        print("\nSync complete!")
    else:
        print("\nAll data already in sync.")


def main():
    if not supabase_db.is_enabled():
        print("ERROR: SUPABASE_URL / SUPABASE_SERVICE_KEY not set")
        sys.exit(1)

    local_regions, local_attacks, local_threat, local_summary = count_local()
    sb_result = count_supabase()

    if isinstance(sb_result, tuple):
        sb_regions, sb_attacks_count = sb_result
    else:
        print("\nCannot compare — Supabase not available")
        sys.exit(1)

    sync_data(local_regions, local_attacks, local_threat, local_summary, sb_regions, sb_attacks_count)

    # Re-check counts after sync
    print("\n" + "=" * 60)
    print("POST-SYNC SUPABASE COUNTS")
    print("=" * 60)
    count_supabase()


if __name__ == "__main__":
    main()
