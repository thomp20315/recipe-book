"""Tiny Supabase REST helper shared by process_queue.py and shopping_queue.py (publishable key is public)."""
import json, urllib.request, urllib.parse
SB_URL = "https://fdxtpbaguqpnislglaur.supabase.co"
SB_KEY = "sb_publishable_FTtpdWJD-TPLVZoFWhcbnQ_M5g0VRCa"

def sb(path, method="GET", body=None, prefer=None):
    h = {"apikey": SB_KEY, "Content-Type": "application/json", "User-Agent": "recipe-book/1.0"}
    if prefer: h["Prefer"] = prefer
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{SB_URL}/rest/v1/{path}", data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            t = r.read().decode()
            return json.loads(t) if t else None
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Supabase error {e.code}: {e.read().decode()[:500]}")

def ids(vals):
    out = []
    for v in vals:
        if not v.isdigit(): raise SystemExit(f"not a numeric id: {v}")
        out.append(v)
    return ",".join(out)
