drop table if exists core.dim_product cascade;

create table core.dim_product as
select
    row_number() over (order by product_name) as product_key,
    product_name                               as name,
    category,
    brand,
    unit_price
from (
    select distinct on (product_name) product_name, category, brand, unit_price
    from stg.orders
    order by product_name
) s;

alter table core.dim_product add primary key (product_key);
