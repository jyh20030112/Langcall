alter table call_tasks
add column if not exists next_attempt_at timestamptz not null default now();

create table if not exists dead_letter_queue (
    id bigserial primary key,
    task_id bigint not null references call_tasks(id) on delete cascade,
    raw_call_id bigint not null references raw_calls(id) on delete cascade,
    call_id varchar(128) not null,
    failed_stage varchar(64) not null,
    error_message text not null,
    payload jsonb not null,
    created_at timestamptz not null default now()
);

create index if not exists idx_call_tasks_next_attempt_at on call_tasks(next_attempt_at);
