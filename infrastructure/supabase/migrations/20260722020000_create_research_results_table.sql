create table if not exists research_results (
    id uuid primary key default gen_random_uuid(),
    research_session_id uuid not null
        references research_sessions (id) on delete cascade,
    opportunity_score integer not null check (opportunity_score between 0 and 100),
    demand_level text not null,
    competition_level text not null,
    profit_level text not null,
    summary text not null,
    created_at timestamp with time zone not null default now(),
    updated_at timestamp with time zone not null default now(),
    constraint research_results_research_session_id_key unique (research_session_id)
);

create trigger research_results_set_updated_at
    before update on research_results
    for each row
    execute function set_updated_at();
