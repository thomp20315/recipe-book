#!/usr/bin/env python3
"""Shopping requests / results (Supabase tables shopping_requests, shopping_results).

  python3 shopping_queue.py list                        # pending requests as JSON
  python3 shopping_queue.py mark <id> processing|done|failed
  python3 shopping_queue.py post-result <request_id> <file.json>   # insert result, mark request done
"""
import json, sys
from sb import sb, ids

a = sys.argv[1:]
if a[:1] == ["list"]:
    print(json.dumps(sb("shopping_requests?status=eq.pending&order=created_at.asc&select=*"), indent=2, ensure_ascii=False))
elif a[:1] == ["mark"] and len(a) == 3 and a[2] in ("pending", "processing", "done", "failed"):
    rows = sb(f"shopping_requests?id=eq.{ids([a[1]])}", "PATCH", {"status": a[2]}, "return=representation")
    print(json.dumps({"updated": [r["id"] for r in rows], "status": a[2]}))
elif a[:1] == ["post-result"] and len(a) == 3:
    rid = ids([a[1]]); result = json.load(open(a[2]))
    if not isinstance(result.get("stores"), list) or not isinstance(result.get("picks"), list):
        sys.exit("result JSON needs 'stores' and 'picks' arrays (see README)")
    req = sb(f"shopping_requests?id=eq.{rid}&select=zip")
    zip_ = result.get("zip") or (req[0]["zip"] if req else None)
    row = sb("shopping_results", "POST", {"request_id": int(rid), "zip": zip_, "result": result}, "return=representation")
    sb(f"shopping_requests?id=eq.{rid}", "PATCH", {"status": "done"}, "return=minimal")
    print(json.dumps({"result_id": row[0]["id"], "request_id": int(rid), "request_status": "done"}))
else:
    sys.exit(__doc__)
