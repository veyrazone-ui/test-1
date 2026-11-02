"""Validate source-package consistency only, not ST syntax or runtime behavior."""
import csv
import hashlib
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PLC = ROOT / "plc"


def check(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main():
    reference = rows(ROOT / "docs/io-map.csv")
    mapped = rows(PLC / "stage2-io-map.csv")
    check(len(mapped) == len(reference), "I/O map row count")
    check(len({r['symbol'] for r in mapped}) == len(mapped), "duplicate I/O symbols")
    by_symbol = {r["symbol"]: r for r in mapped}
    for ref in reference:
        check(ref["symbol"] in by_symbol, "missing symbol " + ref["symbol"])
        mapped_row = by_symbol[ref["symbol"]]
        for key in ("direction", "type", "initial_simulation_value"):
            check(ref[key] == mapped_row[key], f"{ref['symbol']}: {key} mismatch")
        prefix = "PLC_PRG.simInputs." if ref["direction"] == "input" else "PLC_PRG.sorter.o."
        check(mapped_row["manual_watch_path"] == prefix + ref["symbol"], "watch path mismatch")
    for direction, name in (("input", "ST_CellInputs"), ("output", "ST_CellOutputs")):
        source = (PLC / "exports" / (name + ".st")).read_text()
        fields = dict(re.findall(r"(\w+)\s*:\s*BOOL\s*:=\s*(TRUE|FALSE)\s*;", source))
        expected = {r["symbol"]: "TRUE" if r["initial_simulation_value"] == "1" else "FALSE"
                    for r in reference if r["direction"] == direction}
        check(fields == expected, name + " declarations/defaults differ from I/O map")
    print("PASS: all 14 I/O symbols, watch paths, types and source defaults agree")

    expected_objects = {
        "E_CellState": "TYPE", "E_CellFault": "TYPE", "ST_CellInputs": "TYPE",
        "ST_CellOutputs": "TYPE", "ST_Stage2Sample": "TYPE",
        "FB_ConveyorSorter": "FUNCTION_BLOCK", "PLC_PRG": "PROGRAM",
        "PRG_TestSequence": "PROGRAM",
    }
    check({p.stem for p in (PLC / "exports").glob("*.st")} == set(expected_objects),
          "unexpected or missing ST source objects")
    for name, kind in expected_objects.items():
        source = (PLC / "exports" / (name + ".st")).read_text()
        check(re.search(rf"\b{kind}\s+{name}\b", source), "object declaration missing: " + name)
        check(source.rstrip().endswith("END_" + kind), "object terminator missing: " + name)
        if kind != "TYPE":
            check(source.count("(* IMPLEMENTATION:") == 1, "pane marker missing: " + name)
        code = re.sub(r"\(\*.*?\*\)", "", source, flags=re.S)
        check(not re.search(r"\b(RETAIN|PERSISTENT)\b|%[IQM]", code),
              "unexpected retention or physical address: " + name)
    print("PASS: eight source objects have consistent names, boundaries and pane markers")
    print("PASS: no retained variables or physical I/O addresses in supplied ST")

    recorded = (ROOT / "evidence/stage2/source-sha256.txt").read_text()
    actual = "".join(hashlib.sha256(p.read_bytes()).hexdigest() + "  "
                     + p.relative_to(ROOT).as_posix() + "\n"
                     for p in sorted((PLC / "exports").glob("*.st")))
    check(recorded == actual, "source SHA-256 inventory is stale")
    print("PASS: SHA-256 inventory matches all eight ST source files")

    results = rows(ROOT / "evidence/stage2/stage2-results.csv")
    ids = [r["test_id"] for r in results]
    expected_ids = [f"S2-{i:02}" for i in range(1, 26)]
    check(ids == expected_ids, "result register IDs/order")
    guide = (PLC / "stage2-simulation.md").read_text()
    check(re.findall(r"^\| (S2-\d+) \|", guide, re.M) == ids,
          "simulation guide and result register disagree")
    for row in results:
        check(row["status"] in {"NOT RUN", "PASS", "FAIL", "INCONCLUSIVE"}, "invalid status")
        if row["status"] != "NOT RUN":
            check(all(row[k].strip() for k in
                      ("actual", "evidence_path", "operator", "run_date", "source_commit")),
                  "observed result lacks provenance: " + row["test_id"])
    print("PASS: 25 procedure cases have matching result slots and valid evidence status")

    # Check repository-local Markdown links; future evidence paths are plain text,
    # never live links to files that do not exist yet.
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        for target in re.findall(r"\[[^\]]*\]\(([^)\s]+)\)", path.read_text()):
            if "://" in target or target.startswith("#") or target.startswith("mailto:"):
                continue
            target = target.split("#", 1)[0]
            check((path.parent / target).exists(), f"broken local link in {path}: {target}")
    print("PASS: repository-local Markdown links resolve")
    print("LIMIT: no CODESYS compiler/runtime was invoked; PLC validation remains pending")


if __name__ == "__main__":
    main()
