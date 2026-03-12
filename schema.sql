
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


-- Activer RLS sur les deux tables
  ALTER TABLE users ENABLE ROW LEVEL SECURITY;
  ALTER TABLE passwords ENABLE ROW LEVEL SECURITY;

  -- Table users : autoriser INSERT et SELECT pour anon
  CREATE POLICY "anon can insert users" ON users
    FOR INSERT TO anon WITH CHECK (true);

  CREATE POLICY "anon can select users" ON users
    FOR SELECT TO anon USING (true);

  -- Table passwords : autoriser INSERT, SELECT et UPDATE pour anon
  CREATE POLICY "anon can insert passwords" ON passwords
    FOR INSERT TO anon WITH CHECK (true);

  CREATE POLICY "anon can select passwords" ON passwords
    FOR SELECT TO anon USING (true);

  CREATE POLICY "anon can update passwords" ON passwords
    FOR UPDATE TO anon USING (true);