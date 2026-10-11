# Recipe Book
To add a recipe: save its photo to `images/<id>.jpg`, then add an object to `recipes.json` with these fields: id, title, description, servings, prepTime, cookTime, totalTime (leave any of those empty/null if unknown), image, source, sourceName, ingredients[], steps[].
Then run `python3 build.py` and redeploy (`npx surge . <domain>`).

## App (PWA)
`build.py` also generates `manifest.webmanifest`, `sw.js` (offline cache, refreshes when online) and `icons/`. On iPhone: open the site in Safari → Share → Add to Home Screen. On Android: Chrome menu → Install app / Add to Home screen.

## Family ratings
Mom/Dad/Kids star ratings are stored in a shared JSON object on api.restful-api.dev (URL in `RATINGS_URL` in build.py), not in recipes.json, so rebuilds never touch them. The service worker never caches them.

## Pending-recipe queue (Add Recipe button)
The app's **Add Recipe** sheet appends `{url, notes, addedBy?, ts}` to a shared queue record on api.restful-api.dev
(`QUEUE_URL` in build.py, separate from ratings; never cached by the service worker). It re-reads the queue before writing.

- `python3 process_queue.py` prints pending items as JSON.
- `python3 process_queue.py --remove <ts> [<ts> ...]` removes processed items (re-reads first so new submissions aren't clobbered).

Typical flow: list the queue, add each recipe to recipes.json + images/, run `python3 build.py`, commit and push, then `--remove` those ts values.
