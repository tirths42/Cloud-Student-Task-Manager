-- Run this once in Supabase Dashboard > SQL Editor > New query.
create table if not exists public.tasks (
  task_id text primary key,
  title text not null,
  subject text not null default 'General',
  description text not null default '',
  priority text not null check (priority in ('Low','Medium','High')),
  due_date text not null default '',
  is_completed boolean not null default false,
  created_at timestamptz not null,
  updated_at timestamptz not null
);

-- Keep Row Level Security enabled. The Flask server uses the secret service-role
-- key on the server only; never put that key in browser JavaScript or GitHub.
alter table public.tasks enable row level security;
