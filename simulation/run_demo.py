"""Run with: python -m simulation.run_demo --scenario reject --trace trace.csv"""

import argparse
import csv
from pathlib import Path

from simulation.scenarios import run_scenario


def main():
    parser = argparse.ArgumentParser(description="Conveyor controller reference demo")
    parser.add_argument("--scenario", choices=("accept", "reject", "feed-jam", "interlock"), default="accept")
    parser.add_argument("--trace", type=Path, help="Optional full scan trace CSV output")
    args = parser.parse_args()
    controller, rows = run_scenario(args.scenario)
    print(f"scenario={args.scenario} state={controller.state.value} "
          f"accepted={controller.accepted_count} rejected={controller.rejected_count} "
          f"fault={controller.fault or 'NONE'} scans={len(rows)}")
    if args.trace:
        args.trace.parent.mkdir(parents=True, exist_ok=True)
        with args.trace.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f"Trace written to {args.trace}")


if __name__ == "__main__":
    main()
