# PR #2 prepared-source review and corrections

Reviewed 7 November 2026 (Asia/Colombo) against PR head
`160f06428e8ae989b869a61a92e147d5fcd325c3` and current main
`b2a7115347d852f349fb3f84c078e52fce3e5787`.
[Review discussion](https://github.com/veyrazone-ui/test-1/pull/2#pullrequestreview-5763630455).

**Decision:** these corrections prepare the source package for review. Stage 2
remains **OPEN** and all 25 runtime cases remain **NOT RUN**. The PR stays draft;
this work does not merge it or assert CODESYS compilation, IDE execution, measured
timing, native project creation or hardware commissioning.

## High severity — behavior and unsupported validation conclusions

| Finding | Exact correction | Required verification |
| --- | --- | --- |
| Newly raised INVALID_STATE can disappear on a coincident Reset edge | In [FB_ConveyorSorter.st](../plc/exports/FB_ConveyorSorter.st), fault recovery additionally requires `scanState = E_CellState.FAULT`. The detection edge is consumed and cannot recover the new fault. | Prepared S2-18 modes 5 and 6 seed EXTEND/RETRACT before the detection call. Require FAULT/INVALID_STATE/alarm on detection and held-Reset scans; only a later eligible rising edge recovers. Both modes remain NOT RUN. |
| S2-24/S2-25 can report success without proving the intended transition or time boundary | [PRG_TestSequence.st](../plc/exports/PRG_TestSequence.st) asserts the preceding active state, zero count, prior/current sensor values and transition scan. Mode 4 now captures the following scan. Samples record scan-entry state. The flag is `sequence_passed`, explicitly limited to runner assertions. | Inspect previous/event/next samples plus a real timestamped task trace. Require `t_previous < t_completion < t_entry + PT <= t_next`; missing resolution/bracketing means INCONCLUSIVE. No scan-index-derived timestamps. |
| An observed PASS could cite nonexistent evidence and an invalid commit | [check_package.py](../plc/check_package.py) requires nonempty tracked regular evidence under `evidence/stage2/`, rejects traversal/symlinks/package placeholders, validates ISO date and a full commit SHA resolving to an ancestor of HEAD, and compares PASS source bytes to that commit. | [Mutation tests](../tests/test_plc_package.py) reject missing/untracked/empty evidence, unsafe paths, symlinks, invalid/non-commit/unrelated SHAs and stale PASS. A valid synthetic fixture only tests the validator; it is never PLC evidence. |

## Medium severity — reproducibility, integration and coverage

| Finding | Exact correction | Required verification |
| --- | --- | --- |
| Source hashes fail on a fresh `core.autocrlf=true` checkout | Add `*.st text eol=lf` to [.gitattributes](../.gitattributes); retain byte-exact hashing and regenerate the eight-source inventory after ST changes. | Run the checker in an independent fresh checkout with autocrlf enabled; verify ST files contain LF. The workflow also performs this checkout check. |
| Two README conflicts obscure independently completed/planned work | Merge current main into the PR branch and combine both opening status and component-table hunks. Preserve CAD planning files and distinguish Stage 2 source preparation from runtime completion; retain Stage 6 pending artifacts. | No conflict markers or unmerged paths; current main is a parent of the correction commit. README says CAD planning complete; both models, both STEP files, drawing and geometry inspection pending. |
| S2-11 ends before a stale passage latch becomes observable; S2-14 says all outputs off | Extend S2-11 through re-entered ACCEPT with accepted FALSE and station clear, require count 0, then provide a new true-to-false passage. S2-14 lists conveyor/extend/alarm/ready in FAULT and recovered READY. Update guide and CSV together. | These runtime observations remain pending. The package checker now rejects guide/CSV action or expected-result drift. |
| S2-20/S2-21 overstate post-timeout reset and recovery coverage | Mode 0 adds a fresh Start and FEED entry after Stop/Reset. Timeout modes 1/2 capture the next scan with ET=0/Q=FALSE while fault remains. S2-20 separately requires uninterrupted FEED-timeout and ACCEPT-timeout recovery traces, each through Reset, fresh Start and a full new 5 s FEED window. | The [procedure](../plc/stage2-simulation.md) maps every expectation to its capture/scan range. Frozen timeout samples and normal mode 0 do not establish timeout recovery. No cold reset or task switch may bridge the recovery trace. |

## Documentation and CI integration

- [Design mapping](../plc/stage2-mapping.md): scan-entry fault restriction and consumed Reset edge.
- [PLC package](../plc/README.md): seven modes, defensive injection boundary and assertions-versus-timing distinction.
- [Simulation guide](../plc/stage2-simulation.md) and [result register](../evidence/stage2/stage2-results.csv): 25 matching rows; seven modes include two S2-18 subcases, not two new result rows.
- [Evidence register](../evidence/stage2/README.md): exact provenance rules, capture requirements and unchanged OPEN gate.
- [Workflow](../.github/workflows/checks.yml): full history for provenance, Python/validator tests, package check, four demos and independent autocrlf checkout.

## Repository validation and its limit

Validation passed locally: **41 Python tests** (27 reference + 14 evidence-validator
tests), all four demo entry points, package and state/fault mapping checks, and an
independent fresh `core.autocrlf=true` checkout with eight LF ST files. All 25 PLC
rows were checked to remain NOT RUN with empty actual/provenance fields. The CAD
planning files match current main exactly.

Actual command output is retained in [local-checks.txt](../evidence/stage2/local-checks.txt).
The 27 existing tests exercise the Python reference controller. Additional
mutation tests exercise the evidence validator. The package checker examines
source inventory, I/O consistency, guide/register agreement, file/commit integrity
and local links. None of these executes or compiles the Structured Text. The
prepared runner assertions and manual cases must still be run in CODESYS.

A structurally valid evidence record is not authenticated runtime evidence. A
reviewer must examine the native project/archive, compiler messages, exact
versions/task setup and real captures before accepting any PLC result. A source
merge alone must never change Stage 2 to complete.

## Remaining gate

Create the native project/archive and IDE export, rebuild with zero errors and
record warning dispositions, then run all required variations in the 25-case
matrix. Preserve state-injection, interrupted-passage, timeout recovery and
measured-boundary captures with source provenance. Any required NOT RUN, FAIL or
INCONCLUSIVE result keeps Stage 2 OPEN. Reject sequencing and full-cell acceptance
remain Stage 3/4; CAD execution remains Stage 6.
