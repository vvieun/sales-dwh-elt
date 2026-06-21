create schema if not exists core;
drop table if exists core.dim_date cascade;

create table core.dim_date as
select
    row_number() over (order by d)        as date_key,
    d                                     as date_actual,
    extract(year from d)::int             as year,
    extract(quarter from d)::int          as quarter,
    extract(month from d)::int            as month,
    trim(to_char(d, 'Day'))               as weekday
from (select distinct order_date as d from stg.orders) s;

alter table core.dim_date add primary key (date_key);
