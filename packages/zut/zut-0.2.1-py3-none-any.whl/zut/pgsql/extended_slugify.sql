--
-- Requires:
--
--    create extension if not exists unaccent;
--
create or replace function extended_slugify(input text)
returns text as $$
  -- removes accents (diacritic signs) from a given string --
  with "unaccented" as (
    select unaccent(input) as value
  ),
  -- lowercases the string
  "lowercase" as (
    select lower(value) as value
    from "unaccented"
  ),
  -- french special: replace "l'" and "d'" to ensure hyphen will be kept
  "fr_special" as (
    select replace(replace(value, 'l''', 'l-'), 'd''', 'd-') as value
    from "lowercase"
  ),
  -- remove single and double quotes
  "removed_quotes" as (
    select regexp_replace(value, '[''"]+', '', 'gi') as value
    from "fr_special"
  ),
  -- replaces anything that's not a letter or a number, with a hyphen('-')
  "hyphenated" as (
    select regexp_replace(value, '[^a-z0-9]+', '-', 'gi') as value
    from "removed_quotes"
  ),
  -- trims hyphens('-') if they exist on the head or tail of the string
  "trimmed" as (
    select regexp_replace(regexp_replace(value, '\-+$', ''), '^\-+', '') as value
    from "hyphenated"
  )
  select value from "trimmed";
$$ language sql strict immutable;
