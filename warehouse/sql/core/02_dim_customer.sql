drop table if exists core.dim_customer cascade;

create table core.dim_customer as
select
    row_number() over (order by customer_name) as customer_key,
    customer_name                              as name,
    segment,
    city,
    country
from (
    select distinct on (customer_name) customer_name, segment, city, country
    from stg.orders
    order by customer_name
) s;

alter table core.dim_customer add primary key (customer_key);
