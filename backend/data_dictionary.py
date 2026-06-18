"""Schema + categorical-value grounding for the SQL-generation prompt.

Sourced from the official SWITRS dictionary (tims.berkeley.edu/help/SWITRS.php)
and the human-readable value remaps used to build the DB.
"""

SCHEMA_PROMPT = """\
You are querying a DuckDB database of California traffic collisions (SWITRS),
2001-01-01 to 2021-06-03. Four tables, all joinable on `case_id`:

TABLE collisions (one row per crash, ~9.4M rows). Key columns:
- case_id (TEXT, join key)
- collision_date (TEXT 'YYYY-MM-DD'), collision_time (TEXT 'HH:MM:SS')
- county_location (TEXT, lowercase, e.g. 'los angeles', 'orange')
- collision_severity (TEXT): 'property damage only','pain','other injury',
  'severe injury','fatal'
- killed_victims (INT), injured_victims (INT), party_count (INT)
- type_of_collision (TEXT): 'rear end','broadside','sideswipe','hit object',
  'head-on','pedestrian','overturned','other'
- motor_vehicle_involved_with (TEXT): 'other motor vehicle','fixed object',
  'parked motor vehicle','pedestrian','bicycle','animal','train', etc.
  (a parked-vehicle crash is motor_vehicle_involved_with='parked motor vehicle')
- weather_1 (TEXT): 'clear','cloudy','raining','fog','snowing','wind','other'
- lighting (TEXT): 'daylight','dark with street lights',
  'dark with no street lights','dusk or dawn'
- road_surface, road_condition_1, control_device (TEXT)
- pedestrian_collision, bicycle_collision, motorcycle_collision, truck_collision,
  alcohol_involved, hit_and_run, tow_away (BOOLEAN-ish: '1'=yes, ''/NULL=no)
- latitude (REAL), longitude (REAL)

TABLE parties (people/vehicles per crash, ~18.7M rows). Key columns:
- case_id (TEXT, join key), party_number (INT)
- party_type (TEXT), at_fault ('1'=yes), party_sex, party_age (INT)
- party_sobriety (TEXT), party_race (TEXT)
- vehicle_make (TEXT, lowercase e.g. 'toyota','ford'), vehicle_year (INT),
  statewide_vehicle_type (TEXT)
- movement_preceding_collision (TEXT, includes 'parked','making left turn', etc.)
- cellphone_in_use ('1'=yes)

TABLE victims (injured/killed people, ~9.6M rows). Key columns:
- case_id (TEXT, join key), party_number (INT)
- victim_role, victim_sex, victim_age (INT)
- victim_degree_of_injury (TEXT), victim_ejected (TEXT)

TABLE case_ids (case_id TEXT, db_year): maps a case to its source dataset.

RULES:
- Boolean-like flags are stored as TEXT '1' for yes; use `col = '1'`.
- For percentages use 100.0 * SUM(CASE WHEN ... THEN 1 ELSE 0 END) / COUNT(*).
- For day-of-week use strftime('%w', CAST(collision_date AS DATE)) (0=Sunday)
  or dayname(CAST(collision_date AS DATE)).
- For year use strftime('%Y', CAST(collision_date AS DATE)) or
  EXTRACT(year FROM CAST(collision_date AS DATE)).
- County/make/weather values are lowercase.
- Always return aggregated, chart-friendly results when the question is analytical.

DUCKDB DIALECT (important — this is DuckDB, NOT MySQL/Postgres):
- Do NOT use FIELD(), IF(), or other MySQL-only functions.
- To order results by day of week, GROUP BY the numeric weekday and present the
  name, e.g.:
    SELECT dayname(CAST(collision_date AS DATE)) AS day_of_week, COUNT(*) AS n
    FROM collisions
    GROUP BY day_of_week, dayofweek(CAST(collision_date AS DATE))
    ORDER BY dayofweek(CAST(collision_date AS DATE));
  (dayofweek returns 0=Sunday..6=Saturday.)
- Use CASE WHEN ... THEN ... ELSE ... END instead of IF().
- Cast date text with CAST(collision_date AS DATE) before date functions.

JOINS & CTEs (use freely when a question spans tables or has multiple steps):
- All three tables join on case_id: collisions.case_id = parties.case_id =
  victims.case_id. Use `JOIN parties USING (case_id)` etc.
- parties and victims also share party_number within a case; join on BOTH
  case_id AND party_number when matching a specific person to their party:
    JOIN victims v ON p.case_id = v.case_id AND p.party_number = v.party_number
- One collision has many parties and many victims. When counting collisions
  after a join, use COUNT(DISTINCT c.case_id) to avoid fan-out double-counting.
- Prefer WITH (CTE) clauses for multi-step questions (e.g. compute per-group
  totals in one CTE, a filtered subset in another, then join/compare them).
  DuckDB fully supports multiple CTEs, nested CTEs, and subqueries.
- Aggregate or filter inside a CTE before joining the 18.7M-row parties table
  when possible, so the join stays small and fast.
"""


def build_schema_prompt() -> str:
    return SCHEMA_PROMPT
