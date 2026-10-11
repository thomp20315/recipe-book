#!/usr/bin/env python3
"""Add Recipe queue (Supabase table recipe_queue).

  python3 process_queue.py                  # print pending rows as JSON
  python3 process_queue.py --done ID [ID..] # mark rows done
  python3 process_queue.py --reject ID [..] # mark rows rejected (e.g. duplicates)
"""
import json, sys
from sb import sb, ids

a = sys.argv[1:]
if not a:
    print(json.dumps(sb("recipe_queue?status=eq.pending&order=created_at.asc&select=*"), indent=2, ensure_ascii=False))
elif a[0] in ("--done", "--reject") and len(a) > 1:
    st = "done" if a[0] == "--done" else "rejected"
    rows = sb(f"recipe_queue?id=in.({ids(a[1:])})", "PATCH", {"status": st}, "return=representation")
    print(json.dumps({"updated": [r["id"] for r in rows], "status": st}))
else:
    sys.exit(__doc__)
