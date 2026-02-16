
-- Table users
create table users (
  id uuid primary key default gen_random_uuid(),
  session_start timestamp default now()
);

-- Table passwords
create table passwords (
  id serial primary key,
  user_id uuid references users(id),
  value text not null,
  copied boolean default false,
  timestamp timestamp default now(),
  word1 text,
  word2 text,
  numeric integer,
  special_char text,
  batch_id uuid
);
