#!/usr/bin/env python3
"""Quick debug: check attack data freshness."""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"

with open(DATA / "attacks.json") as f:
    attacks = json.load(f)

now = datetime.now(timezone.utc)
one_hour_ago = now - timedelta(hours=1)
two_hours_ago = now - timedelta(hours=2)

print(f"Now UTC: {now.isoformat()}")
print(f"1h ago:  {one_hour_ago.isoformat()}")
print(f"Total attacks: {len(attacks)}")

def parse_ts(raw):
    try:
        ts = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return ts
    except:
        return None

recent_1h = []
recent_2h = []
for a in attacks:
    best_ts = None
    for field in ("published", "fetched_at"):
        ts = parse_ts(a.get(field, ""))
        if ts and (best_ts is None or ts > best_ts):
            best_ts = ts
    if best_ts:
        if best_ts >= one_hour_ago:
            recent_1h.append(a)
        if best_ts >= two_hours_ago:
            recent_2h.append(a)

print(f"Attacks in last 1h: {len(recent_1h)}")
print(f"Attacks in last 2h: {len(recent_2h)}")

print("\nLatest 10 by fetched_at:")
for a in sorted(attacks, key=lambda x: x.get("fetched_at", ""), reverse=True)[:10]:
    fa = a.get("fetched_at", "?")
    pub = a.get("published", "?")
    title = a.get("title_en", "")[:70]
    cat = a.get("classification", {}).get("category", "?")
    sev = a.get("classification", {}).get("severity", "?")
    print(f"  fetched={fa}")
    print(f"  pub={pub}  [{sev}/{cat}]  {title}")
    print()

# Check if pipeline is writing to Supabase instead of local files
print("--- Checking if db.py uses Supabase ---")
db_path = Path(__file__).parent / "db.py"
if db_path.exists():
    content = db_path.read_text()
    if "supabase" in content.lower():
        print("YES - db.py references Supabase")
    else:
        print("NO - db.py does not reference Supabase")
