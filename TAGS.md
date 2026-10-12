# Tags

Allowed set (also free-text custom tags): Kids, Breakfast, Desserts, Holiday Ideas, Coffee, Dinner, Cocktails, Soup, Sides, Crockpot Meals, Lunch, Sauces, Dips, Snacks, Appetizers, Lactation/PP, Bread/Sourdough, Ninja Creami, Juice.

## Shared store
Tags live in Supabase table `recipe_tags` (see `supabase.sql`). Seed values may also appear as an optional `tags` array on each recipe in `recipes.json`; the app overlays the Supabase values at runtime so both phones stay in sync.

## One-time setup
In the Supabase SQL Editor, re-run `supabase.sql` (safe to rerun). That creates `recipe_tags`, its index, RLS, and realtime. Until that runs, the recipe page will show a short note that tags need the database setup, and edits won't persist.

## Add Recipe queue
The Add Recipe sheet can attach a `tags` jsonb array on the queue row. If the column isn't there yet, the app falls back to appending `Tags: …` to the notes field.
