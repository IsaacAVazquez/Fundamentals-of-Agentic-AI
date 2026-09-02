-- Contacts table. Every row belongs to exactly one Neon Auth user.
create table if not exists contacts (
  id          uuid primary key default gen_random_uuid(),
  user_id     text not null default (auth.user_id()),  -- the caller's JWT "sub", filled in by Postgres
  name        text not null check (length(btrim(name)) > 0),
  company     text,
  role        text,
  where_met   text,
  notes       text,
  priority    text not null check (priority in ('high', 'medium', 'low')),
  created_at  timestamptz not null default now()
);

create index if not exists contacts_user_id_idx on contacts (user_id);

-- Row Level Security. The Data API connects as the "authenticated" role, so these policies gate every request.
alter table contacts enable row level security;

drop policy if exists contacts_select on contacts;
create policy contacts_select on contacts for select to authenticated
  using (auth.user_id() = user_id);

drop policy if exists contacts_insert on contacts;
create policy contacts_insert on contacts for insert to authenticated
  with check (auth.user_id() = user_id);

drop policy if exists contacts_update on contacts;
create policy contacts_update on contacts for update to authenticated
  using (auth.user_id() = user_id)        -- may only touch own rows
  with check (auth.user_id() = user_id);  -- and may not hand a row to someone else

drop policy if exists contacts_delete on contacts;
create policy contacts_delete on contacts for delete to authenticated
  using (auth.user_id() = user_id);

-- Table privileges for the Data API role. RLS above narrows them to the caller's own rows.
grant select, insert, update, delete on contacts to authenticated;
