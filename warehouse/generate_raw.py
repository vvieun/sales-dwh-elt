import random
from datetime import date, timedelta

import psycopg2
from psycopg2.extras import execute_values

from .db import DSN

random.seed(42)

SCHEMA = """
create schema if not exists raw;
drop table if exists raw.orders;
create table raw.orders (
    order_id text,
    order_ts text,
    customer_name text,
    customer_segment text,
    city text,
    country text,
    product_name text,
    category text,
    brand text,
    unit_price text,
    quantity text,
    store_name text,
    region text,
    store_country text
);
"""

SEGMENTS = ["Enterprise", "SMB", "Consumer", "Government"]
CATEGORIES = ["Laptops", "Phones", "Monitors", "Audio", "Accessories"]
BRANDS = ["Acme", "Globex", "Initech", "Umbrella", "Soylent"]
REGIONS = ["North", "South", "East", "West"]
CITIES = ["Berlin", "Paris", "Madrid", "Rome", "Warsaw", "Lisbon"]
COUNTRIES = ["Germany", "France", "Spain", "Italy", "Poland", "Portugal"]


def messy(value):
    return random.choice([value, value.upper(), value.lower(), value.title()])


def gen_customers(n=200):
    out = []
    for i in range(1, n + 1):
        c = random.randrange(len(CITIES))
        out.append((f"Customer {i}", random.choice(SEGMENTS), CITIES[c], COUNTRIES[c]))
    return out


def gen_products(n=80):
    return [(f"Product {i}", random.choice(CATEGORIES), random.choice(BRANDS),
             round(random.uniform(20, 2000), 2)) for i in range(1, n + 1)]


def gen_stores(n=15):
    out = []
    for i in range(1, n + 1):
        c = random.randrange(len(COUNTRIES))
        out.append((f"Store {i}", random.choice(REGIONS), COUNTRIES[c]))
    return out


def gen_orders(customers, products, stores, n=5000):
    start = date(2023, 1, 1)
    span = (date(2024, 12, 31) - start).days
    rows = []
    for i in range(1, n + 1):
        day = start + timedelta(days=random.randint(0, span))
        cust = random.choice(customers)
        prod = random.choice(products)
        store = random.choice(stores)
        name = cust[0] + ("  " if random.random() < 0.1 else "")
        country = None if random.random() < 0.03 else cust[3]
        rows.append([
            str(i), day.isoformat(), name, messy(cust[1]), cust[2], country,
            prod[0], messy(prod[1]), messy(prod[2]),
            f"{prod[3]:.2f}", str(random.randint(1, 10)),
            store[0], messy(store[1]), store[2],
        ])
    duplicates = [list(r) for r in random.sample(rows, k=int(n * 0.05))]
    return rows + duplicates


def main():
    customers = gen_customers()
    products = gen_products()
    stores = gen_stores()
    orders = gen_orders(customers, products, stores)

    conn = psycopg2.connect(DSN)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            cur.execute(SCHEMA)
            execute_values(cur, "insert into raw.orders values %s", orders)
        conn.commit()
    finally:
        conn.close()

    print(f"loaded {len(orders)} raw rows (incl. duplicates) into raw.orders")


if __name__ == "__main__":
    main()
