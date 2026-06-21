import pathlib
import sys

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from warehouse import db

CHECKS = pathlib.Path(__file__).resolve().parent / "checks.yaml"
REPORT = pathlib.Path(__file__).resolve().parent / "report.md"


def evaluate():
    checks = yaml.safe_load(CHECKS.read_text())
    results = []
    for name, sql in checks.items():
        _, rows = db.query(sql)
        results.append((name, len(rows) == 0, len(rows)))
        flag = "PASS" if not rows else f"FAIL ({len(rows)} violations)"
        print(f"[{flag}] {name}")
    return results


def reconciliation():
    return {
        "raw rows": db.scalar("select count(*) from raw.orders"),
        "raw distinct orders": db.scalar("select count(distinct order_id) from raw.orders"),
        "stg rows": db.scalar("select count(*) from stg.orders"),
        "fact rows": db.scalar("select count(*) from core.fact_sales"),
        "fact revenue": db.scalar("select round(sum(amount), 2) from core.fact_sales"),
    }


def report(results, recon):
    passed = sum(ok for _, ok, _ in results)
    total = len(results)
    lines = [
        "# Data quality report",
        "",
        f"- checks passed: **{passed}/{total}**",
        "",
        "| check | result | violations |",
        "|-------|--------|------------|",
    ]
    for name, ok, n in results:
        lines.append(f"| {name} | {'pass' if ok else 'fail'} | {n} |")
    lines += ["", "## Reconciliation", ""]
    for k, v in recon.items():
        lines.append(f"- {k}: {v}")

    REPORT.write_text("\n".join(lines) + "\n")
    print("\nreconciliation:")
    for k, v in recon.items():
        print(f"  {k}: {v}")
    print(f"\n{passed}/{total} checks passed — report written to {REPORT}")


if __name__ == "__main__":
    report(evaluate(), reconciliation())
