"""Mutation tests for evidence integrity. These never compile or execute PLC ST."""
import csv
from contextlib import redirect_stdout
import io
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from plc import check_package


class EvidenceValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Evidence validator fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "core.autocrlf", "false")
        self.source = self.root / "plc/exports/Fixture.st"
        self.source.parent.mkdir(parents=True)
        self.source.write_text("(* Synthetic source fixture; no PLC execution. *)\n")
        self.git("add", ".")
        self.git("commit", "-qm", "Synthetic source fixture")
        self.commit = self.git("rev-parse", "HEAD").strip()
        self.evidence = self.root / "evidence/stage2/fixture.txt"
        self.evidence.parent.mkdir(parents=True)
        self.evidence.write_text("Synthetic validator fixture, not a PLC observation.\n")
        self.git("add", "evidence/stage2/fixture.txt")
        self.row = dict(test_id="S2-01", status="PASS", actual="Synthetic fixture only",
                        evidence_path="evidence/stage2/fixture.txt", operator="Test fixture",
                        run_date="2026-11-07", source_commit=self.commit)

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True,
                              capture_output=True, text=True).stdout

    def validate(self, **changes):
        check_package.validate_result(self.root, self.row | changes)

    def test_observed_records_accept_tracked_file_and_real_ancestor_commit(self):
        for status in ("PASS", "FAIL", "INCONCLUSIVE"):
            with self.subTest(status=status):
                self.validate(status=status)

    def test_pending_record_needs_no_git_or_evidence(self):
        row = self.row | dict(status="NOT RUN", actual="", evidence_path="", operator="",
                              run_date="", source_commit="")
        check_package.validate_result(self.root / "absent", row)
        for field in ("actual", "evidence_path", "operator", "run_date", "source_commit"):
            with self.subTest(field=field), self.assertRaisesRegex(SystemExit, "NOT RUN"):
                check_package.validate_result(self.root, row | {field: "invented"})

    def test_observed_records_require_every_provenance_field(self):
        for status in ("PASS", "FAIL", "INCONCLUSIVE"):
            for field in ("actual", "evidence_path", "operator", "run_date", "source_commit"):
                with self.subTest(status=status, field=field):
                    with self.assertRaisesRegex(SystemExit, "lacks provenance"):
                        self.validate(**({"status": status, field: " "}))

    def test_unknown_status_rejected(self):
        with self.assertRaisesRegex(SystemExit, "invalid status"):
            self.validate(status="PASSED")

    def test_missing_empty_directory_and_untracked_evidence_rejected(self):
        with self.assertRaisesRegex(SystemExit, "missing, empty"):
            self.validate(evidence_path="evidence/stage2/missing.txt")
        self.evidence.write_text("")
        with self.assertRaisesRegex(SystemExit, "missing, empty"):
            self.validate()
        self.evidence.unlink()
        self.evidence.mkdir()
        with self.assertRaisesRegex(SystemExit, "not a regular file"):
            self.validate()
        other = self.evidence.parent / "untracked.txt"
        other.write_text("Synthetic, untracked")
        with self.assertRaisesRegex(SystemExit, "tracked regular"):
            self.validate(evidence_path="evidence/stage2/untracked.txt")

    def test_paths_cannot_escape_or_use_ambiguous_separators(self):
        for path in (str(self.evidence), "../outside.txt", "evidence/stage2/../../outside.txt",
                     "evidence/stage2/./fixture.txt", "evidence//stage2/fixture.txt",
                     "evidence\\stage2\\fixture.txt", "C:/evidence/stage2/fixture.txt",
                     "https://example.invalid/trace.csv", "evidence/stage2/fixture.txt ",
                     "evidence/accept-trace.csv"):
            with self.subTest(path=path), self.assertRaisesRegex(SystemExit, "relative path"):
                self.validate(evidence_path=path)

    def test_symlink_file_and_directory_rejected(self):
        link = self.evidence.parent / "link.txt"
        try:
            link.symlink_to(self.evidence)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unavailable on this host")
        with self.assertRaisesRegex(SystemExit, "symlink"):
            self.validate(evidence_path="evidence/stage2/link.txt")
        folder = self.evidence.parent / "linked"
        folder.symlink_to(self.evidence.parent, target_is_directory=True)
        with self.assertRaisesRegex(SystemExit, "symlink"):
            self.validate(evidence_path="evidence/stage2/linked/fixture.txt")
        outside = self.root / "outside.txt"
        outside.write_text("Synthetic external fixture")
        link.unlink()
        link.symlink_to(outside)
        with self.assertRaisesRegex(SystemExit, "escapes"):
            self.validate(evidence_path="evidence/stage2/link.txt")

    def test_package_indexes_are_not_runtime_evidence(self):
        for filename in ("README.md", "stage2-results.csv", "source-sha256.txt", "local-checks.txt"):
            path = self.evidence.parent / filename
            path.write_text("Synthetic package metadata")
            with self.subTest(filename=filename):
                with self.assertRaisesRegex(SystemExit, "not PLC evidence"):
                    self.validate(evidence_path="evidence/stage2/" + filename)

    def test_malformed_and_unknown_commits_rejected(self):
        for commit in ("not-a-commit", self.commit[:7], self.commit.upper(), "0" * 40):
            with self.subTest(commit=commit), self.assertRaises(SystemExit):
                self.validate(source_commit=commit)

    def test_blob_sha_is_not_a_commit(self):
        blob = self.git("rev-parse", "HEAD:plc/exports/Fixture.st").strip()
        with self.assertRaisesRegex(SystemExit, "does not identify a commit"):
            self.validate(source_commit=blob)

    def test_unrelated_commit_is_not_source_provenance(self):
        tree = self.git("rev-parse", "HEAD^{tree}").strip()
        unrelated = self.git("commit-tree", tree, "-m", "Unrelated synthetic root").strip()
        with self.assertRaisesRegex(SystemExit, "Git provenance check failed"):
            self.validate(source_commit=unrelated)

    def test_pass_cannot_be_carried_forward_after_source_change(self):
        self.source.write_text("(* Changed synthetic source. *)\n")
        with self.assertRaisesRegex(SystemExit, "PASS is stale"):
            self.validate()
        # Old failures/captures remain useful; they do not claim the new source passed.
        self.validate(status="FAIL")
        self.validate(status="INCONCLUSIVE")

    def test_calendar_dates_are_validated(self):
        for value in ("yesterday", "2026-2-1", "2026-02-30", "2026-13-01"):
            with self.subTest(value=value), self.assertRaises(SystemExit):
                self.validate(run_date=value)

    def test_guide_and_register_expected_text_must_agree(self):
        fixture = self.root / "package"
        fixture.mkdir()
        for name in ("plc", "docs", "evidence"):
            shutil.copytree(check_package.ROOT / name, fixture / name)
        path = fixture / "evidence/stage2/stage2-results.csv"
        with path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            fields = reader.fieldnames
            records = list(reader)
        records[10]["expected"] = "Old, insufficient latch check"
        with path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(records)
        with patch.object(check_package, "ROOT", fixture), patch.object(check_package, "PLC", fixture / "plc"):
            with redirect_stdout(io.StringIO()), self.assertRaisesRegex(SystemExit, "guide action/case or expected result differs"):
                check_package.main()


if __name__ == "__main__":
    unittest.main()
