create schema if not exists stg;
drop table if exists stg.orders cascade;

create table stg.orders as
select distinct on (order_id)
    order_id::int                         as order_id,
    order_ts::date                        as order_date,
    trim(customer_name)                   as customer_name,
    initcap(trim(customer_segment))       as segment,
    initcap(trim(city))                   as city,
    initcap(trim(country))                as country,
    trim(product_name)                    as product_name,
    initcap(trim(category))               as category,
    initcap(trim(brand))                  as brand,
    unit_price::numeric(10, 2)            as unit_price,
    quantity::int                         as quantity,
    trim(store_name)                      as store_name,
    initcap(trim(region))                 as region,
    initcap(trim(store_country))          as store_country
from raw.orders
where order_id is not null
  and order_ts is not null
  and quantity is not null
  and unit_price is not null
order by order_id;

alter table stg.orders add primary key (order_id);
