-- Adds a project to each item, for the Projects tab.
--
-- Run once in the Supabase SQL editor. Safe to re-run.
-- Only adds one empty column; existing items and values are untouched.
-- The app works without this script and simply hides projects.

alter table inventory_items
    add column if not exists project text;
