# Recipe Book
To add a recipe: save its photo to `images/<id>.jpg`, then add an object to `recipes.json` with these fields: id, title, description, servings, prepTime, cookTime, totalTime (leave any of those empty/null if unknown), image, source, sourceName, ingredients[], steps[].
Then run `python3 build.py` and redeploy (`npx surge . <domain>`).

## App (PWA)
`build.py` also generates `manifest.webmanifest`, `sw.js` (offline cache, refreshes when online) and `icons/`. On iPhone: open the site in Safari → Share → Add to Home Screen. On Android: Chrome menu → Install app / Add to Home screen.

## Shared data (Supabase)
Ratings, the Add Recipe queue, the shopping cart, the zip code and shopping requests/results live in Supabase
(`https://fdxtpbaguqpnislglaur.supabase.co`, publishable key in `build.py` / `sb.py`; it's public by design).
Schema and row-level-security policies: `supabase.sql` (paste into the Supabase SQL Editor; safe to rerun).
None of this is in recipes.json, so rebuilds never touch it, and the service worker never caches it (cross-origin).

| Table | Used for |
|---|---|
| ratings | Mom/Dad/Kids stars (recipe_id, person, stars 1-5) |
| recipe_queue | Links sent from the Add Recipe sheet (url, notes, added_by, status) |
| cart_items | Shared shopping cart (recipe_id or null for custom, text, checked, sort_order) |
| settings | key `zip` = family zip code |
| shopping_requests | "Let's go shopping" taps (zip, items jsonb, requested_by, status) |
| shopping_results | One result per request (`result` jsonb, shape below) |

### Add Recipe queue
- `python3 process_queue.py` prints pending rows as JSON.
- `python3 process_queue.py --done <id> [<id> ...]` marks them done (`--reject` for duplicates).

Flow: list, add each recipe to recipes.json + images/, `python3 build.py`, commit, push, then `--done` the ids.

### Shopping
- `python3 shopping_queue.py list` prints pending shopping requests.
- `python3 shopping_queue.py mark <id> processing|done|failed`
- `python3 shopping_queue.py post-result <request_id> result.json` inserts the result (the cart shows the newest one) and marks the request done.

Result JSON shape (see `shopping_result.example.json`, which is fake sample data). Check a file with `python3 shopping_queue.py validate file.json`.
Older results without the newer fields still render.
```json
{
  "zip": "78602",
  "generated_at": "ISO-8601 timestamp",
  "currency": "USD",
  "stores": [{"id": "heb", "name": "Store", "address": "...", "distance_mi": 1.2,
              "subtotal": 20.47, "coupon_savings": 2.00, "total": 18.47,
              "items_found": 5, "items_missing": ["cart item text"]}],
  "picks":  [{"store": "heb", "item": "cart item text", "product": "Product name", "brand": "Brand",
              "why_clean": "why it's a clean choice", "price": 5.48, "unit": "12 oz", "url": "https://...",
              "coupon": {"description": "$1 off", "savings": 1.00, "source_url": "https://...",
                         "type": "digital | manufacturer | weekly_ad | sale"},
              "final_price": 4.48}],
  "cheapest_store": "heb",
  "top3": ["heb", "walmart", "target"],
  "hybrid": {"stores": ["heb", "walmart"],
             "assignments": [{"item": "cart item text", "store": "heb"}],
             "subtotal": 30.00, "coupon_savings": 2.00, "total": 28.00,
             "savings_vs_best_single": 1.50, "note": "free text"},
  "notes": "free text"
}
```
- `picks[].store`, `cheapest_store`, `top3[]` and `hybrid.stores[]` all refer to `stores[].id`. `coupon` may be `null`. Unknown prices and totals are `null`; never guess.
- The app shows: Cheapest overall (`cheapest_store`, otherwise the lowest-total store with no missing items), the Best 2-store split card when `hybrid` is present, then a Top 3 stores section with expandable cards (each pick's price, coupon line and savings in green, final price, then subtotal, coupons saved and total, plus any missing items), then All stores checked, then notes.
