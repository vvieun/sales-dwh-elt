drop table if exists core.fact_sales cascade;

create table core.fact_sales as
select
    o.order_id                              as sale_id,
    dd.date_key,
    dc.customer_key,
    dp.product_key,
    ds.store_key,
    o.quantity,
    (o.unit_price * o.quantity)::numeric(12, 2) as amount
from stg.orders o
join core.dim_date dd     on dd.date_actual = o.order_date
join core.dim_customer dc on dc.name        = o.customer_name
join core.dim_product dp  on dp.name        = o.product_name
join core.dim_store ds    on ds.name        = o.store_name;

alter table core.fact_sales add primary key (sale_id);
alter table core.fact_sales add foreign key (date_key) references core.dim_date;
alter table core.fact_sales add foreign key (customer_key) references core.dim_customer;
alter table core.fact_sales add foreign key (product_key) references core.dim_product;
alter table core.fact_sales add foreign key (store_key) references core.dim_store;
