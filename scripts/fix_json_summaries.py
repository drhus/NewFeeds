"""Fix articles with raw JSON in summary_en and clear API unavailable placeholders."""
import json
import os
import re

FEEDS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "feeds")

counts = {"json_fixed": 0, "json_partial": 0, "api_cleared": 0}

for fname in sorted(os.listdir(FEEDS_DIR)):
    if not fname.endswith(".json"):
        continue
    fpath = os.path.join(FEEDS_DIR, fname)
    data = json.load(open(fpath))
    changed = False
    for a in data:
        summary = (a.get("summary_en") or "").strip()

        # Fix 1: raw JSON object in summary_en  e.g. {"h":"...", "r":true, "s":"..."}
        if summary.startswith("{"):
            # Try valid JSON first
            try:
                obj = json.loads(summary)
                if isinstance(obj, dict):
                    if "s" in obj:
                        a["summary_en"] = obj["s"]
                    if "h" in obj and not a.get("title_en"):
                        a["title_en"] = obj["h"]
                    if "r" in obj:
                        a["relevant"] = obj["r"]
                    counts["json_fixed"] += 1
                    changed = True
                    continue
            except json.JSONDecodeError:
                pass

            # Truncated JSON — extract fields with regex
            h_match = re.search(r'"h"\s*:\s*"((?:[^"\\]|\\.)*)"', summary)
            s_match = re.search(r'"s"\s*:\s*"((?:[^"\\]|\\.)*)', summary)
            r_match = re.search(r'"r"\s*:\s*(true|false)', summary)

            # Also try matching truncated h (no closing quote)
            if not h_match:
                h_match = re.search(r'"h"\s*:\s*"((?:[^"\\]|\\.)+)', summary)

            extracted = False
            if s_match:
                a["summary_en"] = s_match.group(1)
                extracted = True
            elif h_match:
                a["summary_en"] = h_match.group(1)
                extracted = True

            if h_match and not a.get("title_en"):
                a["title_en"] = h_match.group(1)

            if r_match:
                a["relevant"] = r_match.group(1) == "true"

            if extracted:
                counts["json_partial"] += 1
                changed = True
                continue

        # Fix 2: [API unavailable ...] or [Parse error ...] placeholders
        summary = (a.get("summary_en") or "").strip()
        if re.match(r"^\[API unavailable", summary) or re.match(r"^\[Parse error", summary):
            a["summary_en"] = ""
            counts["api_cleared"] += 1
            changed = True

    if changed:
        with open(fpath, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Fixed: {fname}")

print(f"\nTotal: {counts['json_fixed']} valid JSON extracted, "
      f"{counts['json_partial']} truncated JSON extracted, "
      f"{counts['api_cleared']} placeholders cleared")
