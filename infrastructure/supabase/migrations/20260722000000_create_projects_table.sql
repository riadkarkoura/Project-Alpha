create extension if not exists "pgcrypto";

create table if not exists projects (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    created_at timestamp with time zone not null default now(),
    updated_at timestamp with time zone not null default now()
);

create or replace function set_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

create trigger projects_set_updated_at
    before update on projects
    for each row
    execute function set_updated_at();
