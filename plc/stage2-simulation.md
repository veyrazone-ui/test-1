# Stage 2 CODESYS IDE simulation procedure

**Procedure and expected results only. All PLC runs are NOT RUN as supplied.**
Use CODESYS Development System V3 with its built-in **IDE Simulation** command.
This is not a Python/PLC connection, a SoftPLC installation guide or the separate
CODESYS Simulation Interface product. No physical I/O is mapped.

## 1. Create and compile the application

1. Record repository commit, date, operator, OS, full CODESYS V3 version, compiler
   version, device name/version and resolved Standard library version in
   [the run record](../evidence/stage2/README.md). Do not invent version numbers.
2. File → New Project → Standard Project. Use an installed CODESYS Control Win V3
   device (or the corresponding x64 device supplied by your installation), with
   `PLC_PRG` language Structured Text. Record the actual selection. Save as
   `plc/ConveyorSorting_Stage2.project`.
3. Under Application add DUT enum objects `E_CellState`, `E_CellFault` and structure
   objects `ST_CellInputs`, `ST_CellOutputs`, `ST_Stage2Sample`. Replace each DUT's
   editor text with its corresponding complete `exports/*.st` contents, including
   TYPE/END_TYPE and attributes. Names must match exactly.
4. Add `FB_ConveyorSorter` as a Function Block in ST. Replace the **declaration
   pane** with its file from `FUNCTION_BLOCK` through the last `END_VAR`, before
   the IMPLEMENTATION marker. Paste the remaining implementation into the lower
   ST pane, **omitting the final END_FUNCTION_BLOCK** (the IDE supplies the object
   boundary). Do the same for `PLC_PRG` and new PROGRAM `PRG_TestSequence`, omitting
   their final END_PROGRAM lines. The `.st` files are readable combined source;
   this procedure does not assume arbitrary `.st` file import support.
5. In Library Manager confirm Standard resolves and provides TON/R_TRIG. If it is
   not present, add Standard. Do not replace timers with Python or custom counters.
6. In Task Configuration set `MainTask` Type=Cyclic, Interval=`T#20ms`; keep only
   the `PLC_PRG` call. Record priority and watchdog settings as configured. Remove
   duplicate/freewheeling calls. No other task may call this controller instance.
7. Build → Rebuild. Save the **actual** compiler messages as
   `evidence/stage2/compile-log.txt`, with a task-configuration screenshot. Required
   result: zero errors; investigate and record every warning. Fix source and repeat
   compilation if necessary. A clean package check is not a compiler result.
8. While logged out, choose Online → Simulation; verify the simulation indicator.
   Online → Login, accept creation/loading of the simulated application, then
   use Debug → Start when ready. No communication gateway or physical target
   connection is needed for IDE simulation.

## 2. Manual input and observation setup

Use a Watch list for all paths in [stage2-io-map.csv](stage2-io-map.csv), plus:

```text
PLC_PRG.sorter.state
PLC_PRG.sorter.fault
PLC_PRG.sorter.accepted_count
PLC_PRG.sorter.rejected_count
PLC_PRG.sorter.accepted_seen
PLC_PRG.sorter.start_edge
PLC_PRG.sorter.reset_edge
PLC_PRG.sorter.feed_et
PLC_PRG.sorter.accept_et
PLC_PRG.sorter.feed_q
PLC_PRG.sorter.accept_q
```

Write prepared **input** values; do not force state, counters, outputs or timer
internals to create a pass. No forces should remain active. If using Force Values
for an exploratory input test, remove all forces before the next case and record
that choice. Prefer Write Values so a lingering force cannot override the runner.

For a new independent manual case: Stop the IDE application, release all forces,
use IDE Reset Cold, verify the input defaults, then Start the IDE application.
This is distinct from the Boolean operator `stop`, `reset` and `start` inputs.
Unless stated otherwise, pulse means write TRUE for at least three task cycles,
then FALSE for at least three cycles. One-scan edge diagnostics may be invisible
at the Watch refresh rate; use the trace/runner for scan-level evidence.

“Arm” means pulse operator Reset with clear path, Start/Stop FALSE and healthy
permissive: expected READY with both movement commands FALSE. “Begin” means arm,
then pulse operator Start: expected FEED. “Enter ACCEPT” means begin, then write
station=TRUE with metal=FALSE before 5 s; expected ACCEPT.

## 3. Manual test matrix

Each row is an independent cold run unless it explicitly continues a cycle.
Complete inputs before the relevant 5 s/3 s deadline; use the scripted normal run
if manual entry is too slow. Counts below begin at zero unless specified. For
each case record actual state, fault, outputs, count, trace path and PASS/FAIL.

| ID | Action | Expected result |
| --- | --- | --- |
| S2-01 | Cold start, then pulse Start before Reset | STOPPED, count 0, commands off; Start does not arm |
| S2-02 | Arm; continue holding Reset for several scans | READY, count 0, commands off; no repeated action |
| S2-03 | In STOPPED assert Reset+Start together; clear Start while Reset stays TRUE; then release/repress Reset | Remains STOPPED until new eligible Reset; then READY, no motion |
| S2-04 | READY: assert Reset+Start together; release Reset while Start stays TRUE; release/repress Start | No motion until the fresh Start; then FEED. This READY inhibit is stricter than Python |
| S2-05 | Begin holding Start TRUE; enter ACCEPT; accepted TRUE with station TRUE; clear station while accepted stays TRUE; clear accepted | No count while accepted high; final READY, accepted_count=1, rejected_count=0, commands off |
| S2-06 | Continue S2-05, holding Start TRUE for at least 0.2 s, then release/repress Start | Stays READY/count 1 while held; fresh edge begins next FEED without adding a count |
| S2-07 | Enter ACCEPT; accepted TRUE then FALSE while station stays TRUE; then clear station | Count stays 0 until station clear; then READY/count 1 |
| S2-08 | Enter ACCEPT; clear station, never assert accepted; wait beyond 3 s | FAULT/ACCEPT_TIMEOUT, count 0, commands off |
| S2-09 | Enter ACCEPT; accepted TRUE and station FALSE; keep accepted high beyond 3 s | FAULT/ACCEPT_TIMEOUT, count 0; held high is not passage |
| S2-10 | Begin; never assert station; wait beyond 5 s | FAULT/FEED_TIMEOUT, count 0, commands off |
| S2-11 | Repeat Stop interruption in FEED and ACCEPT (in ACCEPT first set accepted TRUE). Clear path, release Stop; pulse Reset then Start | Same evaluated Stop scan is STOPPED/commands off; no count. Release alone cannot restart; Reset gives READY only; fresh Start required. Old passage memory cannot complete the new cycle |
| S2-12 | Enter FEED/ACCEPT separately; pulse Reset while moving with Start released | State/route unchanged, no count caused by Reset; normal phase timer continues, not restarted |
| S2-13 | FEED/ACCEPT separately: permissive FALSE; restore permissive, clear path; apply Stop and then release | FAULT/INTERLOCK_OPEN, commands off, count unchanged; restoration and Stop do not erase fault; eligible Reset required |
| S2-14 | Fault via permissive loss, restore it but keep station TRUE; hold Reset TRUE; then clear station; release/repress Reset | Blocked/held Reset leaves FAULT; new eligible edge → READY; outputs off |
| S2-15 | First complete one accept; Stop and Reset; begin another cycle, interrupt with permissive loss, clear path and Reset | Completed accepted_count remains 1 through all recovery; interrupted cycle adds nothing |
| S2-16 | Begin, set station=TRUE and metal=TRUE | FAULT/METAL_ROUTE_NOT_IMPLEMENTED, commands off, both counts 0; no reject implementation claimed |
| S2-17 | Enter ACCEPT with metal FALSE; then toggle metal TRUE and finish passage | Route remains ACCEPT; normal completion counts exactly once |
| S2-18 | Independent runs: both limits TRUE; both exits TRUE; lose home in FEED/ACCEPT; any exit in FEED; reject exit in ACCEPT | Respectively LIMIT_CONFLICT, EXIT_CONFLICT, PUSHER_NOT_HOME, UNEXPECTED_EXIT; commands off, no count |
| S2-19 | READY, block station then press Start. Clear path; set permissive FALSE and Stop TRUE | First fault START_NOT_CLEAR remains latched despite new conditions. Restore all, release Start/Stop, new Reset → READY |
| S2-20 | Observe phase entry, exit, Stop, fault and recovery across above runs | Entry ET=0; no carry-over; inactive timer resets by next scan; trace proves timer-call order. New FEED has a fresh 5 s window |

Use one dedicated manual sequence for the nominal 1.8 s station-to-accept travel if
desired; manual tests and scripted tests do not validate the proposed mechanics.

## 4. Deterministic replay and deadline cases

Log out. Replace the task call with **only `PRG_TestSequence`**, rebuild and log in
to IDE simulation. Remove all forces. For **every case**, stop the application,
Reset Cold, write `PRG_TestSequence.testCase` while stopped, then Run. Do not change
the case during a run; changing case or Stop/Run without Reset Cold does not
restart its counter or controller. Observe `done`, `passed`, `failed`, `scan`,
`dut` and `samples`. These flags are outputs from the test, not evidence until run.

The runner writes all ten inputs, calls its private DUT once per active scan and
stores the post-call sample in `samples[scan]`. When done it freezes the array;
it is not a continuously executing process controller. Samples are bounded at
301 rows. Copy/export the used samples or capture the relevant rows and save the
actual observations. Restore `PLC_PRG` for subsequent manual tests.

| ID | testCase | Scripted stimulus / nominal scan | Expected terminal result |
| --- | ---: | --- | --- |
| S2-21 | 0 | Reset at 1, held Start from 2, station at 3, accepted high 4–5, both clear 6; Stop 9, Reset 10; finish 12 | passed=TRUE; READY/count 1; no repeat while Start held; no motion on Reset |
| S2-22 | 1 | FEED enters 2; station arrives 252 (nominal elapsed 5000 ms) | FAULT/FEED_TIMEOUT, feed_q=TRUE, count 0; timeout wins |
| S2-23 | 2 | ACCEPT enters 3; accepted high 4–152 and clears 153 (nominal 3000 ms) | FAULT/ACCEPT_TIMEOUT, accept_q=TRUE, count 0; timeout wins |
| S2-24 | 3 | Station arrives 251 (nominal FEED 4980 ms); accepted high 252, clear 253 | ACCEPT at 251 with feed_q=FALSE; terminal READY/count 1 |
| S2-25 | 4 | ACCEPT enters 3; accepted high 4–151, clear 152 (nominal 2980 ms) | READY/count 1, accept_q=FALSE at completion |

For S2-22–25 a nominal scan number is **not proof of a timed boundary**. Review the
prior/current samples, actual ET/Q and task Monitoring jitter. If jitter changes
the outcome, retain the failure, label the timing comparison INCONCLUSIVE, and
investigate/repeat; do not relabel it PASS or alter timeout presets to force it.
To substantiate “same-scan timeout wins”, the capture must show completion input
arriving while that timer's Q is TRUE in that scan. To substantiate “one scan
early”, record the actual adjacent task timestamps and ET below PT on completion.
Add a CODESYS Trace sampled by MainTask for inputs, state, Q/ET, outputs and count
when the installed target supports it. Record any measured offset from the ideal
20 ms model. Never use manual mouse timing to claim an exact deadline test.

For timer-reset S2-20, use a manual continuous run or the S2-21 samples; a runner
freezing on a timeout cannot supply a post-timeout reset scan.

## 5. Save evidence and decide the gate

Copy results into [stage2-results.csv](../evidence/stage2/stage2-results.csv) and
[README.md](../evidence/stage2/README.md). Expected rows and baseline Python logs
must never be renamed to actual PLC traces. Retain compiler log, task screenshot,
startup/held-Start/passage trace, timer/boundary observations, and failed results
with any fix commit. Save the native `.project`, a dependency `.projectarchive`
using the IDE's project archive command, and a native IDE export alongside the
readable source. Add actual filenames and version numbers to the evidence index.

Minimum Stage 2 gate: zero compile errors, documented warnings/task setup, verified
startup/Reset/Start behavior, FEED→ACCEPT, exactly one confirmed count, held-input
and timeout behavior, with native project and actual evidence attached. Keep the
gate OPEN if any required test is NOT RUN, FAIL or INCONCLUSIVE. Stage 3 reject
handling and Stage 4 full-cell acceptance remain separate gates.

## Official references used for this procedure

- [Testing in Simulation Mode](https://content.helpme-codesys.com/en/CODESYS%20Development%20System/_cds_testing_in_simulation_mode.html)
- [Simulation command and limitations](https://content.helpme-codesys.com/en/CODESYS%20Development%20System/_cds_cmd_simulation.html)
- [Cyclic task configuration](https://content.helpme-codesys.com/en/CODESYS%20Development%20System/_cds_f_reference_task.html)
- [Standard TON](https://content.helpme-codesys.com/en/libs/Standard/3.5.15.0/Timer/TON.html)
- [Standard trigger library](https://content.helpme-codesys.com/en/libs/Standard/3.5.22.0/Trigger/fld-Trigger.html)

Consulted 2 November 2026. These explain the IDE and library semantics; they do
not certify this code. IDE simulation runs inside the development process and
does not establish real-time hardware behavior or physical I/O operation.
