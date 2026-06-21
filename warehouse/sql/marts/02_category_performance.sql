drop table if exists mart.category_performance;

create table mart.category_performance as
select
    dp.category,
    sum(f.amount)                                              as revenue,
    round(100 * sum(f.amount) / sum(sum(f.amount)) over (), 2) as revenue_share_pct,
    sum(f.quantity)                                            as units,
    round(avg(f.amount), 2)                                    as avg_order_amount
from core.fact_sales f
join core.dim_product dp using (product_key)
group by dp.category
order by revenue desc;
