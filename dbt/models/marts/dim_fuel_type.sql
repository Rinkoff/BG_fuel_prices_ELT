-- Dimension: one row per fuel type, with a label and unit.
-- fuel_key is a surrogate key (artificial id) the fact table will join on.

with fuels as (

    select distinct fuel_code
    from {{ ref('stg_fuel_prices') }}

)

select
    md5(fuel_code) as fuel_key,          -- surrogate key
    fuel_code,                           -- natural key: 'e95' / 'diesel'
    case fuel_code
        when 'e95'    then 'Бензин A95'
        when 'diesel' then 'Дизел'
        else fuel_code
    end as fuel_label,                   -- human-readable (for the dashboard)
    'EUR/l' as unit
from fuels
