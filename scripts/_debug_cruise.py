#!/usr/bin/env python3
"""Debug: find cruise passengers article in Supabase."""
import db

client = db.get_client()

# Search by title_en
result = client.from_("articles").select(
    "id,title_en,title_original,region,relevant,translated,published,fetched_at"
).ilike("title_en", "%cruise%").execute()

print(f"By title_en: {len(result.data)} rows")
for r in result.data:
    print(f"  region={r.get('region')} relevant={r.get('relevant')} translated={r.get('translated')}")
    print(f"  title_en={str(r.get('title_en',''))[:120]}")
    print(f"  published={r.get('published')} fetched={r.get('fetched_at')}")
    print()

# Search by title_original
result2 = client.from_("articles").select(
    "id,title_en,title_original,region,relevant,translated,published,fetched_at"
).ilike("title_original", "%cruise%").execute()

print(f"By title_original: {len(result2.data)} rows")
for r in result2.data:
    print(f"  region={r.get('region')} relevant={r.get('relevant')} translated={r.get('translated')}")
    print(f"  title_original={str(r.get('title_original',''))[:120]}")
    print()

# Also check: how many total western articles exist?
result3 = client.from_("articles").select(
    "id,title_en,region,relevant,translated,fetched_at", count="exact"
).eq("region", "western").eq("translated", True).not_("relevant", "is", False).order("fetched_at", desc=True).limit(10).execute()

print(f"\nWestern articles (relevant+translated): {result3.count} total, showing latest 10:")
for r in result3.data:
    print(f"  {r.get('fetched_at')} | {str(r.get('title_en',''))[:80]}")
