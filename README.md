# Recipe Book
To add a recipe: save its photo to `images/<id>.jpg`, then add an object to `recipes.json` with these fields: id, title, description, servings, prepTime, cookTime, totalTime (leave any of those empty/null if unknown), image, source, sourceName, ingredients[], steps[].
Then run `python3 build.py` and redeploy (`npx surge . <domain>`).

## App (PWA)
`build.py` also generates `manifest.webmanifest`, `sw.js` (offline cache, refreshes when online) and `icons/`. On iPhone: open the site in Safari → Share → Add to Home Screen. On Android: Chrome menu → Install app / Add to Home screen.

## Family ratings
Mom/Dad/Kids star ratings are stored in a shared JSON object on api.restful-api.dev (URL in `RATINGS_URL` in build.py), not in recipes.json, so rebuilds never touch them. The service worker never caches them.
