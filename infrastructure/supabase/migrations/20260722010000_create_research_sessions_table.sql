create type marketplace as enum ('amazon', 'ebay', 'tiktok');

create table if not exists research_sessions (
    id uuid primary key default gen_random_uuid(),
    project_id uuid not null references projects (id) on delete cascade,
    marketplace marketplace not null,
    status text not null default 'pending'
        check (status in ('pending', 'running', 'completed', 'failed')),
    created_at timestamp with time zone not null default now(),
    updated_at timestamp with time zone not null default now()
);

create index if not exists research_sessions_project_id_idx on research_sessions (project_id);
create index if not exists research_sessions_status_idx on research_sessions (status);

create trigger research_sessions_set_updated_at
    before update on research_sessions
    for each row
    execute function set_updated_at();
