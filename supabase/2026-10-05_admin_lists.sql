-- Creates the table behind the Admin tab, where members, locations,
-- categories, subteams and projects are added and removed in the app.
--
-- Run once in the Supabase SQL editor. Safe to re-run.
-- Only adds a new table; existing items and history are untouched.
-- Until it has been run, the app uses the lists in options.py and the
-- Admin tab shows a setup notice.

begin;

-- Lists edited on the Admin tab
create table if not exists inventory_options (
    list_name text not null,
    value text not null,
    position integer not null default 0,
    created_at timestamptz not null default now(),
    primary key (list_name, value)
);

-- Same lockdown as the other tables: only the server's secret key reads it.
alter table inventory_options enable row level security;

-- Start from the lists currently in options.py
insert into inventory_options (list_name, value, position) values
    ('members', 'Member A', 0),
    ('members', 'Member B', 1),
    ('members', 'Member C', 2),
    ('members', 'Member D', 3),
    ('locations', 'Member A', 0),
    ('locations', 'Member B', 1),
    ('locations', 'Member C', 2),
    ('locations', 'Member D', 3),
    ('locations', 'Club Storage', 4),
    ('categories', 'Fasteners', 0),
    ('categories', 'Electronics', 1),
    ('categories', 'Connectors', 2),
    ('categories', 'Sensors', 3),
    ('categories', 'Motors/Thrusters', 4),
    ('categories', 'Raw Materials', 5),
    ('categories', 'Tools', 6),
    ('categories', 'Waterproofing', 7),
    ('categories', 'Fabricated Parts', 8),
    ('categories', 'Misc.', 9),
    ('subteams', 'F-P', 0),
    ('subteams', 'EPS', 1),
    ('subteams', 'TMS', 2),
    ('subteams', 'GNC', 3),
    ('subteams', 'C-C', 4),
    ('projects', 'ROV build', 0),
    ('projects', 'Competition', 1),
    ('projects', 'Pool testing', 2),
    ('projects', 'Training', 3),
    ('projects', 'Spares', 4)
on conflict (list_name, value) do nothing;

commit;
