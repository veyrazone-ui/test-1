# Stage 2 evidence register

**Gate: OPEN. Source authored; native CODESYS compile and simulation NOT RUN.**
Package updated on 2 November 2026, continuing draft PR #2 (previous head
`58b523eede5140ca54a20d2d8d56792f5029a3e3`), from main baseline
`b4ae9c8e9a807e83dc25c779da03d02f277d8354`.

## Evidence supplied

| Item | Actual status | Evidence / interpretation |
| --- | --- | --- |
| Source integrity | SHA-256 inventory | [source-sha256.txt](source-sha256.txt); identifies this source revision only |
| Stage 2 ST implementation | Authored, reviewable source | [PLC package](../../plc/README.md); not a compiler-generated export |
| I/O/state/fault mapping | Written | [Design](../../plc/stage2-mapping.md), [I/O CSV](../../plc/stage2-io-map.csv) |
| CODESYS procedure and expected results | Written | [25 cases](../../plc/stage2-simulation.md), including five runner modes |
| Python reference regression | See actual local check log | [local-checks.txt](local-checks.txt); validates Python only |
| Source-package consistency | See actual local check log | I/O declarations, object inventory, evidence slots and local links; not ST parsing |
| Native CODESYS project / archive | Not created | Must be created with the IDE and retained after build/run |
| CODESYS compile | NOT RUN | No compiler available in the preparation environment |
| CODESYS runtime cases | NOT RUN | [stage2-results.csv](stage2-results.csv): all actual fields intentionally empty |
| Actual PLC trace / screenshots | Not captured | Source and expected results must not be presented as observations |
| Hardware / electrical / mechanical commissioning | Not performed; out of scope | No claim |

The preparation environment supplies Python 3.12.14, but no CODESYS, Wine or
`iec2c` executable was found on PATH. Local Python results cannot establish ST
syntax correctness, library resolution, task timing or PLC behavior. No compiled
project or screenshots have been fabricated.

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

## Files to add after genuine IDE work

These are **future filenames**, not existing evidence:

- `plc/ConveyorSorting_Stage2.project`
- `plc/ConveyorSorting_Stage2.projectarchive`
- `plc/ConveyorSorting_Stage2.export` (or actual IDE export format)
- `evidence/stage2/compile-log.txt`
- `evidence/stage2/task-configuration.png`
- `evidence/stage2/startup-accept-actual.csv` (or clearly labelled actual capture)
- `evidence/stage2/timer-boundaries-actual.csv` and timing observations
- `evidence/stage2/ide-run-notes.md`

Retain the actual source/export associated with the tested commit. If paste or
compile fixes are needed, commit them and rerun affected tests before updating
README status. Stage 2 only closes when the documented compile/runtime evidence
exists and all required cases pass. This does not close Stage 3/4 or certify a
physical conveyor, safety function, CAD model or machine commissioning.
