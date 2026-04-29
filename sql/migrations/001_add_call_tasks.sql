create table if not exists call_tasks (
    id bigserial primary key,
    raw_call_id bigint not null unique references raw_calls(id) on delete cascade,
    call_id varchar(128) not null,
    task_status varchar(32) not null default 'pending',
    retry_count integer not null default 0,
    locked_by varchar(128),
    last_error text,
    started_at timestamptz,
    completed_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_call_tasks_status_created_at on call_tasks(task_status, created_at);
