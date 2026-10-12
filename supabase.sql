-- Thompson Recipe Book: Supabase schema. Safe to rerun.
-- Paste into Supabase Dashboard -> SQL Editor -> Run.

create extension if not exists pgcrypto;

-- Ratings: one row per recipe + person
create table if not exists public.ratings (
  id          bigint generated always as identity primary key,
  recipe_id   text not null,
  person      text not null check (person in ('mom','dad','kids')),
  stars       smallint not null check (stars between 1 and 5),
  updated_at  timestamptz not null default now(),
  unique (recipe_id, person)
);

-- Add Recipe queue (links submitted from the app)
create table if not exists public.recipe_queue (
  id          bigint generated always as identity primary key,
  url         text not null check (url ~* '^https?://'),
  notes       text not null default '',
  added_by    text check (added_by in ('Mom','Dad','Kids')),
  status      text not null default 'pending' check (status in ('pending','done','rejected')),
  created_at  timestamptz not null default now()
);

-- Shared shopping cart
create table if not exists public.cart_items (
  id            uuid primary key default gen_random_uuid(),
  recipe_id     text,                       -- null = custom item
  recipe_title  text,
  text          text not null check (length(trim(text)) > 0),
  checked       boolean not null default false,
  sort_order    double precision not null default extract(epoch from now()),
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

-- Simple key/value settings (e.g. key 'zip')
create table if not exists public.settings (
  key         text primary key,
  value       text,
  updated_at  timestamptz not null default now()
);

-- Shopping requests ("Let's go shopping")
create table if not exists public.shopping_requests (
  id            bigint generated always as identity primary key,
  zip           text check (zip ~ '^[0-9]{5}$'),
  items         jsonb not null default '[]'::jsonb,   -- [{text, recipe_id, recipe_title}]
  requested_by  text,
  status        text not null default 'pending' check (status in ('pending','processing','done','failed')),
  created_at    timestamptz not null default now()
);

-- Shopping results (store comparisons, products, links, prices)
create table if not exists public.shopping_results (
  id          bigint generated always as identity primary key,
  request_id  bigint references public.shopping_requests(id) on delete set null,
  zip         text,
  result      jsonb not null,
  created_at  timestamptz not null default now()
);

create index if not exists cart_items_sort_idx on public.cart_items (sort_order);
alter table public.recipe_queue add column if not exists tags jsonb not null default '[]'::jsonb;
create index if not exists recipe_queue_status_idx on public.recipe_queue (status, created_at);
create index if not exists shopping_requests_status_idx on public.shopping_requests (status, created_at);
-- Tags (shared, editable in the app)
create table if not exists public.recipe_tags (
  recipe_id   text primary key,
  tags        jsonb not null default '[]'::jsonb,
  updated_at  timestamptz not null default now()
);
create index if not exists recipe_tags_gin on public.recipe_tags using gin (tags);

create index if not exists shopping_results_created_idx on public.shopping_results (created_at desc);

-- Keep updated_at current
create or replace function public.touch_updated_at() returns trigger
language plpgsql as $$ begin new.updated_at := now(); return new; end $$;

drop trigger if exists ratings_touch on public.ratings;
create trigger ratings_touch before update on public.ratings
  for each row execute function public.touch_updated_at();
drop trigger if exists cart_items_touch on public.cart_items;
create trigger cart_items_touch before update on public.cart_items
  for each row execute function public.touch_updated_at();
drop trigger if exists recipe_tags_touch on public.recipe_tags;
create trigger recipe_tags_touch before update on public.recipe_tags
  for each row execute function public.touch_updated_at();
drop trigger if exists settings_touch on public.settings;
create trigger settings_touch before update on public.settings
  for each row execute function public.touch_updated_at();

-- RLS: private family app -> anon/publishable role gets full CRUD on these tables only
do $$
declare t text;
begin
  foreach t in array array['ratings','recipe_queue','cart_items','settings','shopping_requests','shopping_results','recipe_tags'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('grant select, insert, update, delete on public.%I to anon, authenticated', t);
    execute format('drop policy if exists family_all on public.%I', t);
    execute format('create policy family_all on public.%I for all to anon, authenticated using (true) with check (true)', t);
  end loop;
end $$;

-- Identity sequences need usage for inserts
grant usage, select on all sequences in schema public to anon, authenticated;

-- Realtime (live updates across phones); skips tables already added
do $$
declare t text;
begin
  if exists (select 1 from pg_publication where pubname = 'supabase_realtime') then
    foreach t in array array['ratings','recipe_queue','cart_items','settings','shopping_requests','shopping_results','recipe_tags'] loop
      if not exists (select 1 from pg_publication_tables
                     where pubname = 'supabase_realtime' and schemaname = 'public' and tablename = t) then
        execute format('alter publication supabase_realtime add table public.%I', t);
      end if;
    end loop;
  end if;
end $$;

-- Refresh the REST API schema cache
notify pgrst, 'reload schema';
