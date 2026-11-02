# Stage 2 evidence register

Prepared 2 November 2026 against upstream `b4ae9c8e9a807e83dc25c779da03d02f277d8354`.
**Source package delivered; Stage 2 acceptance gate OPEN.**

| Item | Actual status |
| --- | --- |
| Accept-route Structured Text, I/O/state mapping | Written; source review only |
| IDE setup, manual matrix and simulation stimulus driver | Written; expected outcomes, not execution evidence |
| Existing Python reference regression suite | See [local-checks.txt](local-checks.txt); these tests do not execute ST |
| Source hashes and repository package checks | See [source-sha256.txt](source-sha256.txt) and local log; integrity checks only |
| CODESYS compiler/version/library resolution | NOT RUN; CODESYS is unavailable in the authoring environment |
| Native project and dependency archive | NOT CREATED |
| CODESYS IDE simulation, TON timing and boundary behavior | NOT RUN |
| Actual PLC traces, screenshots and build log | NOT CAPTURED |
| Physical I/O, hardware commissioning and machine safety validation | OUT OF SCOPE; not performed |

The [result register](stage2-results.csv) deliberately contains NOT_RUN for every CODESYS test. Expected values in [the procedure](../../plc/stage2-simulation.md) are not actual observations. No generated reference trace has been relabeled as a PLC trace.

## Fill in after an actual IDE run

- Tested repository commit and source hashes:
- Date/operator:
- OS, CODESYS service pack/patch and compiler:
- Device description/version and Standard library resolved version:
- MainTask interval, priority, watchdog and actual timing observations:
- Build errors/warnings, reviewed warnings and build log path:
- Native project/archive paths:
- Selected test driver scenario/arrival scan (or manual case):
- Actual outcomes, discrepancies and evidence paths in CSV:

Suggested future evidence paths (not present and not claimed): `build-messages.txt`, `task-20ms.png`, `normal-cycle.csv`, `feed-timeout.csv`, `accept-held.csv`, `feed-before-deadline.csv`, `feed-at-deadline.csv`, `accept-before-deadline.csv`, `accept-at-deadline.csv`. Native project/archive belong under `plc/`. Add actual exports and links when created; do not add empty placeholder binaries.

Keep failures and inconclusive timing runs visible. When the same test has several subcases, add rows with suffixes such as S2-02a. Each before/at deadline run needs its own actual elapsed-time observation. The result CSV's NOT_RUN status must be replaced only after execution, not after code inspection.

## Open verification points

1. Verify declarations and implementation compile with the chosen CODESYS/Standard versions.
2. Verify the intentional transition-time second TON calls start/reset timers in that scan; verify entry ET=0 and no phase carry-over.
3. Confirm same-scan timeout priority from decision snapshots and a task-sampled trace. IDE jitter may make nominal scan-boundary arrivals inconclusive.
4. Run every Stage 2 case, including fresh Start/Reset edges, held sensors, interruption and count preservation. No hidden assumption that source review proves these.
5. Save the native project/archive and actual exported source, then update the main README only to the level demonstrated.

The source is assistance-produced portfolio material. Reproducing the build/tests and explaining the decisions is the next learning milestone; source delivery alone does not establish individual PLC proficiency.
