-- Staging: light clean-up over the raw table.
-- One row per (week, fuel). Materialized as a view (see dbt_project.yml).

with source as (

    select * from {{ source('raw', 'fuel_prices') }}

),

cleaned as (

    select
        cast(price_date as date)    as price_date,
        lower(fuel_code)            as fuel_code,
        cast(price_eur as double)   as price_eur
    from source
    where price_eur is not null     -- drop weeks with no reported price

)

select * from cleaned
