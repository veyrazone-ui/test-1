# Stage 2 evidence register

**Gate: OPEN. Source authored; native CODESYS compile and simulation NOT RUN.**
Prepared-source corrections reviewed on 7 November 2026 against PR #2 head
`160f06428e8ae989b869a61a92e147d5fcd325c3` and main
`b2a7115347d852f349fb3f84c078e52fce3e5787`. See the
[severity-grouped review and correction record](../../docs/stage2-pr2-review.md).
The source inventory identifies the corrected ST bytes; repository checks are
separate from the still-unrun CODESYS gate.

## Evidence supplied

| Item | Actual status | Evidence / interpretation |
| --- | --- | --- |
| Source integrity | SHA-256 inventory | [source-sha256.txt](source-sha256.txt); identifies this source revision only |
| Stage 2 ST implementation | Authored, reviewable source | [PLC package](../../plc/README.md); not a compiler-generated export |
| I/O/state/fault mapping | Written | [Design](../../plc/stage2-mapping.md), [I/O CSV](../../plc/stage2-io-map.csv) |
| CODESYS procedure and expected results | Written | [25 cases](../../plc/stage2-simulation.md), including seven runner modes (two are S2-18 defensive subcases) |
| Python reference and evidence-validator regression | See actual local check log | [local-checks.txt](local-checks.txt); 27 controller tests plus evidence-validator mutation tests; no ST execution |
| Source-package consistency | See actual local check log | I/O declarations, object inventory, matching guide/CSV expectations, provenance rules and local links; not ST parsing |
| Native CODESYS project / archive | Not created | Must be created with the IDE and retained after build/run |
| CODESYS compile | NOT RUN | No compiler available in the preparation environment |
| CODESYS runtime cases | NOT RUN | [stage2-results.csv](stage2-results.csv): all actual fields intentionally empty |
| Actual PLC trace / screenshots | Not captured | Source and expected results must not be presented as observations |
| Hardware / electrical / mechanical commissioning | Not performed; out of scope | No claim |

The preparation run uses Python; its exact version and outputs are in the local
check log. CODESYS compilation and IDE execution have not been performed. Local
Python results cannot establish ST syntax correctness, library resolution, task
timing or PLC behavior. No compiled project or screenshots have been fabricated.

## Record for the first IDE run

Fill with actual information; pending values are intentionally not guessed.

| Field | Value |
| --- | --- |
| Tested source commit | PENDING |
| Operator / date | PENDING |
| OS and CODESYS full version / architecture | PENDING |
| Compiler version | PENDING |
| Device name / description version | PENDING |
| Resolved Standard library version | PENDING |
| Task name / interval / priority / watchdog | PENDING (required interval: T#20ms) |
| Task entry POU per case | PENDING (PLC_PRG or PRG_TestSequence, exactly one) |
| IDE Simulation indicator verified | PENDING |
| Native project / archive / IDE export filenames | PENDING |
| Compilation errors / warnings and dispositions | PENDING |
| Input writing / forcing method and force cleanup | PENDING |
| Observed cycle time / jitter / timer offsets | PENDING |
| Capture method / trace sampling task | PENDING |

For every S2 case fill actual result, status, evidence path, operator, date and
source commit in the CSV. Split multi-condition rows into separate observations
in an attached run note so each variation is evidenced. PASS means all variations
in that row passed. A timing run affected by jitter can be INCONCLUSIVE; preserve
its capture and explain the limitation. Never copy expected text into actual
without observing it.

## Result provenance rules

For an observed PASS, FAIL or INCONCLUSIVE row, `evidence_path` is one canonical
repository-relative path under `evidence/stage2/`, using `/`, to a nonempty regular
file. Add it to Git before checking. URLs, absolute paths, traversal, symlinks,
untracked files and the package index/register/hash/local-check log are rejected.
Use one primary run note linking the real capture files when a case has several
subcases (especially S2-18/S2-20). Every variation needs its capture and scan/time
range; a note alone cannot establish that a runtime test passed.

`source_commit` must be the full lowercase 40-character Git commit SHA, available
in this clone and an ancestor of HEAD, containing the tested ST sources. Use a
full clone (`git fetch --unshallow` if needed). PASS additionally requires the
current ST bytes to match that commit, so a source change cannot silently retain
an old pass. Preserve earlier failed/inconclusive observations with their original
commit and captures. `run_date` must be a valid ISO date (`YYYY-MM-DD`). NOT RUN
requires all actual/provenance fields to remain empty.

These checks enforce file/commit integrity; they cannot authenticate a file's
contents, confirm the operator's assertions, or prove CODESYS ran. A reviewer must
inspect the native project, compiler output, run context and actual traces. A
local package-check PASS or runner `sequence_passed` never closes Stage 2.

## Files to add after genuine IDE work

These are **future filenames**, not existing evidence:

- `plc/ConveyorSorting_Stage2.project`
- `plc/ConveyorSorting_Stage2.projectarchive`
- `plc/ConveyorSorting_Stage2.export` (or actual IDE export format)
- `evidence/stage2/compile-log.txt`
- `evidence/stage2/task-configuration.png`
- `evidence/stage2/startup-accept-actual.csv` (or clearly labelled actual capture)
- `evidence/stage2/timer-boundaries-actual.csv` and timing observations
- `evidence/stage2/ide-run-notes.md` (including the S2-20 capture-to-expectation map)
- continuous FEED-timeout and ACCEPT-timeout recovery captures, each through a new full FEED window
- timestamped deadline traces with entry/previous/event/next scans, clock resolution and uncertainty
- modes 5/6 invalid-state detection/held-Reset/later-recovery captures

Retain the actual source/export associated with the tested commit. If paste or
compile fixes are needed, commit them and rerun affected tests before updating
README status. Stage 2 only closes when the documented compile/runtime evidence
exists and all required cases pass. This does not close Stage 3/4 or certify a
physical conveyor, safety function, CAD model or machine commissioning.
