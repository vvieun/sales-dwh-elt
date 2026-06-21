import pathlib

from . import db

SQL = pathlib.Path(__file__).resolve().parent / "sql"
LAYERS = ["staging", "core", "marts"]


def run():
    for layer in LAYERS:
        for path in sorted((SQL / layer).glob("*.sql")):
            db.execute(path.read_text())
            print(f"applied {layer}/{path.name}")
    print()
    _counts()


def _counts():
    _, rows = db.query(
        """
        select table_schema, table_name
        from information_schema.tables
        where table_schema in ('raw', 'stg', 'core', 'mart')
        order by array_position(array['raw', 'stg', 'core', 'mart'], table_schema::text), table_name
        """
    )
    names = [f"{s}.{t}" for s, t in rows]
    width = max(len(n) for n in names)
    for name in names:
        print(f"  {name:<{width}}  {db.scalar(f'select count(*) from {name}')}")


if __name__ == "__main__":
    run()
