-- Move existing inventory rows from the old subsystem names to the
-- Oceanus subteams (F-P, EPS, TMS, GNC, C-C).
-- Run once in the Supabase SQL editor. Safe to re-run.
-- Keep this mapping in sync with LEGACY_SUBTEAMS in options.py.

begin;

-- Preview: how many rows each old value has.
select subsystem, count(*)
from inventory_items
group by subsystem
order by subsystem;

update inventory_items
set subsystem = case subsystem
    when 'Mechanical'      then 'F-P'
    when 'Propulsion'      then 'F-P'
    when 'Manipulator'     then 'F-P'
    when 'Waterproofing'   then 'F-P'
    when 'Electrical'      then 'EPS'
    when 'Tether'          then 'TMS'
    when 'Controls'        then 'GNC'
    when 'Cameras/Sensors' then 'C-C'
    else subsystem
end
where subsystem in (
    'Mechanical', 'Propulsion', 'Manipulator', 'Waterproofing',
    'Electrical', 'Tether', 'Controls', 'Cameras/Sensors'
);

-- Anything left here (for example 'General') still needs a subteam.
select id, name, subsystem
from inventory_items
where subsystem not in ('F-P', 'EPS', 'TMS', 'GNC', 'C-C')
   or subsystem is null;

commit;
