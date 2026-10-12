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
| recipe_tags | Shared tags per recipe (`tags` jsonb string array); editable in the app |
| shopping_results | One result per request (`result` jsonb, shape below) |

### Add Recipe queue
- `python3 process_queue.py` prints pending rows as JSON.
- `python3 process_queue.py --done <id> [<id> ...]` marks them done (`--reject` for duplicates).

Flow: list, add each recipe to recipes.json + images/, run `--done <queue_id>=<recipe_id>` (copies the submitted tags into recipes.json and marks it done), then `python3 build.py`, commit, push.

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

## Clean score (shopping results)

The family buys clean, minimally processed food. Every pick in a shopping result can carry a `clean_score` (0-100) and
`ingredient_flags[]`, and every store a `clean_score`. `shopping_queue.py validate` checks both (flag names must come from
the rubric). The rubric and its helpers live in `clean.py`.

| Flag | Penalty | Examples |
|---|---|---|
| `palm_or_seed_oil` | -20 | palm shortening, soybean, canola, corn, sunflower, safflower oil |
| `added_sugar` | -15 | cane or beet sugar, corn syrup, dextrose |
| `dough_conditioner_emulsifier` | -15 | DATEM, ammonium sulfate, SSL, mono- and diglycerides, soy lecithin |
| `gum_stabilizer` | -10 | guar, xanthan, locust bean or carob gum, agar, anti-caking starch or cellulose |
| `artificial_additive_preservative` | -20 | artificial colors or flavors, calcium propionate, sorbates, sulfites, natamycin |
| `minor_aid` | -3 | added enzymes, ascorbic or citric acid, calcium chloride, yeast extract, caramel color |
| `non_organic` | -15 | non-organic produce, meat or dairy where it matters (onion, garlic and citrus exempt; 100% grass-fed beef and pasture-raised eggs count) |
| `ultra_processed` | -10 | industrial formulations such as commercial white sub rolls |

* **Pick score:** start at 100, subtract each flag once, floor at 0. Example: H-E-B Bakery White Sub Rolls
  (palm shortening, beet sugar, dough conditioners, ammonium sulfate, monoglycerides, guar gum) score 27.
* **Store score:** mean of core-item pick scores whose ingredient labels were verified. Pantry and optional items are excluded.
  Missing items get weight 0 and are listed in `items_missing`. Unverified labels are marked `ingredients_checked: false`.
* **Ranking:** `value = total × (1 + 0.5 × (100 − store score)/100)` plus the cheapest other-store price of any missing item.
  Lower is better. A score of 80 adds 10% to the total.
* **In-store swaps:** swap to a cleaner product when it has the lowest `final_price + $0.25 × (100 − clean_score)`.
  Each clean point is worth 25¢, so a cleaner pick wins unless the price gap is large.
* **2-store split (John's rule: cleanest first, then price):**
  1. For every pair of stores (all four, including Sprouts and Target), take the cleanest available pick for each core line.
     Picks within 3 points of that line's best score count as tied, and the cheapest tied pick wins. A store missing an item
     leaves that line to its partner.
  2. The pair's score is the mean of its chosen picks. Choose the pair with the highest score. Pairs within 2 points of the best
     count as tied, and the lowest total wins.
  3. Report the pair's score and total, plus `savings_vs_best_single` against the cleanest single store (highest store
     `clean_score`), labelled with `savings_label`.

The cart shows the score as a small ring on each store and on the 2-store split (green 85+, amber 65-84, red below 65).
Each pick shows a score pill, its flags and any swap.
