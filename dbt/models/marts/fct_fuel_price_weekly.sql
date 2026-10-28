-- Fact: the centre of the star. One row per (week, fuel).
-- Carries the measure (price_eur) and foreign keys to the two dimensions.

with prices as (

    select * from {{ ref('stg_fuel_prices') }}

)

select
    -- surrogate PRIMARY key of the fact: unique per week x fuel
    md5(cast(price_date as varchar) || '-' || fuel_code) as price_key,

    -- FOREIGN keys: same md5() the dimensions used, so they join
    md5(fuel_code)                   as fuel_key,   -- -> dim_fuel_type.fuel_key
    md5(cast(price_date as varchar)) as date_key,   -- -> dim_date.date_key

    price_date,                                      -- kept for convenience
    price_eur                                        -- the measure
from prices
