create table if not exists raw_calls (
    id bigserial primary key,
    call_id varchar(128) not null unique,
    source varchar(64) not null default 'txt_demo',
    file_name varchar(255) not null,
    customer_phone varchar(32),
    customer_email varchar(255),
    transcript_raw text not null,
    created_at timestamptz not null default now()
);

create table if not exists call_analysis (
    id bigserial primary key,
    raw_call_id bigint references raw_calls(id) on delete cascade,
    call_id varchar(128) not null,
    llm_raw_output text,
    summary text,
    sentiment varchar(32),
    follow_up_needed boolean,
    key_points jsonb,
    next_action text,
    parsed_output jsonb not null,
    created_at timestamptz not null default now()
);

create index if not exists idx_raw_calls_created_at on raw_calls(created_at);
create index if not exists idx_call_analysis_call_id on call_analysis(call_id);
