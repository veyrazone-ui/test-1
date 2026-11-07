"""Validate source-package consistency only, not ST syntax or runtime behavior."""
import csv
import hashlib
from datetime import date
from pathlib import Path, PurePosixPath
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PLC = ROOT / "plc"


def check(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def git(root, *args):
    """Read local Git objects only; never fetch or execute shell input."""
    result = subprocess.run(["git", "-C", str(root), *args],
                            capture_output=True, check=False)
    check(result.returncode == 0,
          "Git provenance check failed (use a full clone): " + " ".join(args))
    return result.stdout


def validate_result(root, row):
    """Check record integrity; this cannot authenticate a claimed PLC observation."""
    label = row["test_id"]
    status = row["status"]
    fields = ("actual", "evidence_path", "operator", "run_date", "source_commit")
    check(status in {"NOT RUN", "PASS", "FAIL", "INCONCLUSIVE"}, label + ": invalid status")
    if status == "NOT RUN":
        check(not any(row.get(k, "").strip() for k in fields),
              label + ": NOT RUN must have empty actual/provenance fields")
        return
    check(all(row.get(k, "").strip() for k in fields),
          "observed result lacks provenance: " + label)

    run_date = row["run_date"]
    check(re.fullmatch(r"\d{4}-\d{2}-\d{2}", run_date), label + ": use ISO date YYYY-MM-DD")
    try:
        date.fromisoformat(run_date)
    except ValueError:
        check(False, label + ": invalid calendar date")

    relative = row["evidence_path"]
    path = PurePosixPath(relative)
    check(relative == relative.strip() and relative == path.as_posix()
          and not path.is_absolute() and ".." not in path.parts
          and "\\" not in relative and ":" not in relative
          and path.parts[:2] == ("evidence", "stage2"),
          label + ": evidence must be a repository-relative path under evidence/stage2")
    root = root.resolve()
    evidence = root.joinpath(*path.parts)
    check(evidence.resolve().is_relative_to(root / "evidence/stage2"),
          label + ": evidence escapes its directory")
    cursor = root
    for part in path.parts:
        cursor = cursor / part
        check(not cursor.is_symlink(), label + ": symlink evidence is not accepted")
    check(evidence.is_file() and evidence.stat().st_size > 0,
          label + ": evidence file is missing, empty or not a regular file")
    check(relative not in {"evidence/stage2/README.md", "evidence/stage2/stage2-results.csv",
                           "evidence/stage2/source-sha256.txt", "evidence/stage2/local-checks.txt"},
          label + ": a package index or local check log is not PLC evidence")
    tracked = git(root, "ls-files", "--stage", "--", relative).decode().splitlines()
    check(len(tracked) == 1 and tracked[0].startswith("100644 "),
          label + ": evidence must be a tracked regular file (git add it before checking)")

    commit = row["source_commit"]
    check(re.fullmatch(r"[0-9a-f]{40}", commit), label + ": source_commit must be a full lowercase SHA-1")
    check(git(root, "cat-file", "-t", commit).strip() == b"commit",
          label + ": source_commit does not identify a commit")
    git(root, "merge-base", "--is-ancestor", commit, "HEAD")
    source_paths = sorted((root / "plc/exports").glob("*.st"))
    check(source_paths, label + ": no ST source inventory")
    for source in source_paths:
        saved = git(root, "show", commit + ":" + source.relative_to(root).as_posix())
        if status == "PASS":
            check(saved == source.read_bytes(),
                  label + ": PASS is stale; source differs from the tested commit")


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
        source = (PLC / "exports" / (name + ".st")).read_text(encoding="utf-8")
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
        source = (PLC / "exports" / (name + ".st")).read_text(encoding="utf-8")
        check(re.search(rf"\b{kind}\s+{name}\b", source), "object declaration missing: " + name)
        check(source.rstrip().endswith("END_" + kind), "object terminator missing: " + name)
        if kind != "TYPE":
            check(source.count("(* IMPLEMENTATION:") == 1, "pane marker missing: " + name)
        code = re.sub(r"\(\*.*?\*\)", "", source, flags=re.S)
        check(not re.search(r"\b(RETAIN|PERSISTENT)\b|%[IQM]", code),
              "unexpected retention or physical address: " + name)
    print("PASS: eight source objects have consistent names, boundaries and pane markers")
    print("PASS: no retained variables or physical I/O addresses in supplied ST")

    recorded = (ROOT / "evidence/stage2/source-sha256.txt").read_text(encoding="utf-8")
    actual = "".join(hashlib.sha256(p.read_bytes()).hexdigest() + "  "
                     + p.relative_to(ROOT).as_posix() + "\n"
                     for p in sorted((PLC / "exports").glob("*.st")))
    check(recorded == actual, "source SHA-256 inventory is stale")
    print("PASS: SHA-256 inventory matches all eight ST source files")

    results = rows(ROOT / "evidence/stage2/stage2-results.csv")
    ids = [r["test_id"] for r in results]
    expected_ids = [f"S2-{i:02}" for i in range(1, 26)]
    check(ids == expected_ids, "result register IDs/order")
    guide = (PLC / "stage2-simulation.md").read_text(encoding="utf-8")
    guide_rows = [line.split("|")[1:-1] for line in guide.splitlines()
                  if re.match(r"^\| S2-\d+ \|", line)]
    check([r[0].strip() for r in guide_rows] == ids,
          "simulation guide and result register disagree")
    for row, guide_row in zip(results, guide_rows):
        check(row["procedure_or_case"] == guide_row[1].strip()
              and row["expected"] == guide_row[-1].strip(),
              row["test_id"] + ": guide action/case or expected result differs from CSV")
        validate_result(ROOT, row)
    print("PASS: 25 procedure cases match the register actions/expectations and evidence rules")

    # Check repository-local Markdown links; future evidence paths are plain text,
    # never live links to files that do not exist yet.
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        for target in re.findall(r"\[[^\]]*\]\(([^)\s]+)\)", path.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#") or target.startswith("mailto:"):
                continue
            target = target.split("#", 1)[0]
            check((path.parent / target).exists(), f"broken local link in {path}: {target}")
    print("PASS: repository-local Markdown links resolve")
    print("LIMIT: no CODESYS compiler/runtime was invoked; PLC validation remains pending")


if __name__ == "__main__":
    main()
