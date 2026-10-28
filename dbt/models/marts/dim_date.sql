-- Dimension: one row per bulletin week, enriched with calendar attributes
-- so the dashboard can group by year / month / quarter easily.

with dates as (

    select distinct price_date as date_day
    from {{ ref('stg_fuel_prices') }}

)

select
    md5(cast(date_day as varchar)) as date_key,      -- surrogate key
    date_day,                                         -- the actual date
    extract(year    from date_day) as year,
    extract(month   from date_day) as month,
    extract(quarter from date_day) as quarter,
    monthname(date_day)            as month_name
from dates
