[English](README.md) · [Русский](README.ru.md)

# elt-warehouse

End-to-end data mart

 elt pipeline `raw - staging - core - marts` for postgresql. 
 
 It builds a star schema and aggregate marts from raw, denormalized (flat, not split into tables) source data. Automated data quality tests check that the result is correct.

## Contents

- [Architecture](#architecture)
- [Data Model](#data-model)
- [Stack](#stack)
- [Data](#data)
- [Example Run](#example-run)
- [Quality Checks](#quality-checks)
- [Configuration](#configuration)
- [Notes](#notes)

## Architecture

![lineage](docs/lineage.en.png)

Layers:
- **raw** raw sources (`warehouse/generate_raw.py`);
- **staging** (`warehouse/sql/staging`) sets data types, runs `trim`/`initcap`, removes duplicates by key, and drops bad rows in `stg.orders`;
- **core** (`warehouse/sql/core`) star schema: dimensions with surrogate keys (`row_number`) and the `fact_sales` fact table with foreign keys;
- **marts** (`warehouse/sql/marts`) aggregate marts (`daily_revenue`, `category_performance`).

The names of the layers and of the files inside them set the order (`01_…`, `02_…`).

The runner `warehouse/pipeline.py` applies them one by one. Each step does `drop/create`.

## Data Model

![star](docs/star.png)

## Stack

python, postgresql.

## Data

The `raw.orders` source looks like an export from a live operational system. It is one flat table. All fields are text. The casing is mixed (`Laptops`/`LAPTOPS`/`laptops`). Names have extra spaces. Numbers are stored as strings. The country is sometimes `null`. About 5% of the rows are duplicates. From this source the pipeline rebuilds a clean star schema.

## Example Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

docker compose up -d
python -m warehouse.generate_raw
python -m warehouse.pipeline
```

The `pipeline` output shows the row counts for each layer:

```
  raw.orders                 5250
  stg.orders                 5000
  core.dim_customer          200
  core.dim_date              730
  core.dim_product           80
  core.dim_store             15
  core.fact_sales            5000
  mart.category_performance  5
  mart.daily_revenue         730
```

## Quality Checks

```bash
python -m tests.run
```

This runs the sql checks from `tests/checks.yaml` (each one must return 0 bad rows) and a cross-layer reconciliation (check between layers).

It covers: staging dedup, no nulls in fact keys, unique surrogate keys and `sale_id`, referential integrity from the fact to the dimensions, sum reconciliation (`fact.amount` == `stg`), and no amounts that are zero or negative.

The report is saved to `tests/report.md`. A real example:

- checks passed: **8/8**

| check | result | violations |
|-------|--------|------------|
| staging_dedup | pass | 0 |
| fact_no_null_keys | pass | 0 |
| fact_unique_sale_id | pass | 0 |
| dim_customer_unique_key | pass | 0 |
| ref_integrity_date | pass | 0 |
| ref_integrity_product | pass | 0 |
| amount_reconciliation | pass | 0 |
| no_negative_amounts | pass | 0 |

- raw rows: 5250
- raw distinct orders: 5000
- stg rows: 5000
- fact rows: 5000
- fact revenue: 27695556.03
```

## Configuration

| variable | default |
|------------|--------------|
| `database_url` | `postgresql://dwh:dwh@localhost:5432/dwh` |

## Notes

The natural keys of the dimensions are business names (`customer_name`, `product_name`, `store_name`). In a real warehouse you should replace them with stable source codes. You should also add support for slowly changing dimensions (scd2) and incremental loading, instead of rebuilding everything each time.
