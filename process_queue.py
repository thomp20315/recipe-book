#!/usr/bin/env python3
"""Pending-recipe queue for the Thompson Recipe Book.

  python3 process_queue.py                 # print pending items as JSON
  python3 process_queue.py --remove TS ... # remove processed items by their ts (re-reads first)
"""
import json, sys, time, urllib.request

QUEUE_URL = "https://api.restful-api.dev/objects/ff808181a09d98f701a12cce0b7140bb"
NAME = "thompson-recipe-book-queue"

def _req(method, body=None):
    url = QUEUE_URL + (f"?t={int(time.time()*1000)}" if method == "GET" else "")
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": "application/json", "Cache-Control": "no-cache", "User-Agent": "recipe-book-queue/1.0"})
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.load(resp)

def read():
    d = _req("GET").get("data") or {}
    p = d.get("pending")
    return p if isinstance(p, list) else []

def remove(ts_list):
    want = {str(t) for t in ts_list}
    fresh = read()  # re-read right before writing so new submissions aren't lost
    keep = [i for i in fresh if str(i.get("ts")) not in want]
    removed = len(fresh) - len(keep)
    if removed:
        _req("PUT", {"name": NAME, "data": {"pending": keep}})
    return removed, keep

if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--remove":
        if len(a) < 2: sys.exit("usage: process_queue.py --remove TS [TS ...]")
        n, keep = remove(a[1:])
        print(json.dumps({"removed": n, "remaining": len(keep)}))
    elif a:
        sys.exit(__doc__)
    else:
        print(json.dumps(read(), indent=2, ensure_ascii=False))
