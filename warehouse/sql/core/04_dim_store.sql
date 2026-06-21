drop table if exists core.dim_store cascade;

create table core.dim_store as
select
    row_number() over (order by store_name) as store_key,
    store_name                              as name,
    region,
    store_country                           as country
from (
    select distinct on (store_name) store_name, region, store_country
    from stg.orders
    order by store_name
) s;

alter table core.dim_store add primary key (store_key);
