create table if not exists daily_reports (
    id bigserial primary key,
    report_date date not null,
    report_timezone varchar(64) not null,
    total_calls integer not null default 0,
    positive_count integer not null default 0,
    neutral_count integer not null default 0,
    negative_count integer not null default 0,
    mixed_count integer not null default 0,
    follow_up_count integer not null default 0,
    subject varchar(255) not null,
    recipients text not null,
    html_content text not null,
    send_status varchar(32) not null default 'success',
    error_message text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (report_date, report_timezone)
);

create index if not exists idx_daily_reports_date_timezone on daily_reports(report_date, report_timezone);
