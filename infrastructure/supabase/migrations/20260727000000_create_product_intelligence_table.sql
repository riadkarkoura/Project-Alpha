create table if not exists product_intelligence (
    id uuid primary key default gen_random_uuid(),
    project_id uuid not null references projects (id) on delete cascade,
    research_session_id uuid references research_sessions (id) on delete set null,
    title text not null,
    subtitle text,
    description text,
    features jsonb not null default '[]'::jsonb,
    specifications jsonb not null default '[]'::jsonb,
    category text,
    tags jsonb not null default '[]'::jsonb,
    keywords jsonb not null default '[]'::jsonb,
    seo_metadata jsonb not null default '{}'::jsonb,
    pricing jsonb,
    image_metadata jsonb not null default '[]'::jsonb,
    publishing_metadata jsonb not null default '{}'::jsonb,
    status text not null default 'draft'
        check (status in ('draft', 'ready_for_publishing', 'published')),
    created_at timestamp with time zone not null default now(),
    updated_at timestamp with time zone not null default now()
);

create index if not exists product_intelligence_project_id_idx on product_intelligence (project_id);
create index if not exists product_intelligence_research_session_id_idx
    on product_intelligence (research_session_id);
create index if not exists product_intelligence_status_idx on product_intelligence (status);

create trigger product_intelligence_set_updated_at
    before update on product_intelligence
    for each row
    execute function set_updated_at();
