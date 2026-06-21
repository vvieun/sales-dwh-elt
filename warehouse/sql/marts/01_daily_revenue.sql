create schema if not exists mart;
drop table if exists mart.daily_revenue;

create table mart.daily_revenue as
select
    dd.date_actual,
    dd.year,
    dd.month,
    count(*)            as orders,
    sum(f.quantity)     as units,
    sum(f.amount)       as revenue
from core.fact_sales f
join core.dim_date dd using (date_key)
group by dd.date_actual, dd.year, dd.month
order by dd.date_actual;
