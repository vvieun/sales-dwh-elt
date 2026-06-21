# elt-warehouse

End-to-end витрина данных

 elt-пайплайн `raw - staging - core - marts` для postgresql. 
 
 Из сырых денормализованных источников строится звёздная схема и витрины-агрегаты, корректность проверяется автоматическими тестами качества данных.

## Содержание

- [Архитектура](#архитектура)
- [Модель данных](#модель-данных)
- [Стек](#стек)
- [Данные](#данные)
- [Пример запуска](#пример-запуска)
- [Проверки качества](#проверки-качества)
- [Конфигурация](#конфигурация)
- [Заметки](#заметки)

## Архитектура

![lineage](docs/lineage.png)

Слои:
- **raw** сырые источники (`warehouse/generate_raw.py`);
- **staging** (`warehouse/sql/staging`) типизация, `trim`/`initcap`, дедупликация по ключу, отсев битых строк в `stg.orders`;
- **core** (`warehouse/sql/core`) звёздная схема: измерения с суррогатными ключами (`row_number`) и факт `fact_sales` с внешними ключами;
- **marts** (`warehouse/sql/marts`) витрины-агрегаты (`daily_revenue`, `category_performance`).

Порядок слоёв и файлов внутри задаётся именами (`01_…`, `02_…`).

Раннер `warehouse/pipeline.py` применяет их по очереди. Каждый шаг `drop/create`.

## Модель данных

![star](docs/star.png)

## Стек

python, postgresql.

## Данные

Источник `raw.orders` имитирует выгрузку из операционной системы, где одна плоская таблица, все поля текстом, разный регистр (`Laptops`/`LAPTOPS`/`laptops`), лишние пробелы в именах, числа строками, изредка `null` в стране и ~5% дублирующих строк. Из неё дальше восстанавливается нормализованная звёздная схема.

## Пример запуска

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

docker compose up -d
python -m warehouse.generate_raw
python -m warehouse.pipeline
```

Вывод `pipeline` показывает число строк по слоям:

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

## Проверки качества

```bash
python -m tests.run
```

Прогоняет sql-ассерты из `tests/checks.yaml` (каждый должен вернуть 0 строк-нарушений) и сверку слоёв.

Покрыто: дедуп staging, отсутствие null в ключах факта, уникальность суррогатных ключей и `sale_id`, ссылочная целостность факта на измерения, сходимость суммы (`fact.amount` == `stg`), отсутствие неположительных сумм.

Отчёт пишется в `tests/report.md`. Реальный пример:

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

## Конфигурация

| переменная | по умолчанию |
|------------|--------------|
| `database_url` | `postgresql://dwh:dwh@localhost:5432/dwh` |

## Заметки

Натуральные ключи измерений - бизнес-имена (`customer_name`, `product_name`, `store_name`). В реальном хранилище их стоит заменить на устойчивые коды источника и добавить обработку медленно меняющихся измерений (scd2) и инкрементальную загрузку вместо полной пересборки.
