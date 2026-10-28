-- Singular test: a price must be strictly positive.
-- A dbt test PASSES when this query returns zero rows.

select price_key, price_eur
from {{ ref('fct_fuel_price_weekly') }}
where price_eur <= 0
