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
internals to create a pass. The sole defensive exception is the labelled
reserved-state injection in runner modes 5/6 for S2-18; it seeds the private test
instance before the detection call and records its entry state. It is not normal
operator recovery or production logic. No forces should remain active. If using Force Values
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
| S2-11 | Repeat Stop interruption in FEED and ACCEPT (first set accepted TRUE in the interrupted ACCEPT). Clear path, release Stop; pulse Reset then fresh Start; re-enter ACCEPT with accepted FALSE, clear station and hold accepted FALSE for at least three cycles. Then supply a new accepted TRUE then FALSE before timeout | Stop gives STOPPED/conveyor=FALSE/extend=FALSE with count 0; Reset gives READY only. On re-entered ACCEPT, count remains 0 with accepted FALSE and station clear; only the NEW true-to-false passage gives READY/count 1. No stale passage latch |
| S2-12 | Enter FEED/ACCEPT separately; pulse Reset while moving with Start released | State/route unchanged, no count caused by Reset; normal phase timer continues, not restarted |
| S2-13 | FEED/ACCEPT separately: permissive FALSE; restore permissive, clear path; apply Stop and then release | FAULT/INTERLOCK_OPEN, commands off, count unchanged; restoration and Stop do not erase fault; eligible Reset required |
| S2-14 | Fault via permissive loss, restore it but keep station TRUE; hold Reset TRUE; then clear station; release/repress Reset | Blocked/held Reset leaves FAULT: conveyor=FALSE, extend=FALSE, alarm=TRUE, ready=FALSE. A new eligible edge gives READY: conveyor=FALSE, extend=FALSE, alarm=FALSE, ready=TRUE |
| S2-15 | First complete one accept; Stop and Reset; begin another cycle, interrupt with permissive loss, clear path and Reset | Completed accepted_count remains 1 through all recovery; interrupted cycle adds nothing |
| S2-16 | Begin, set station=TRUE and metal=TRUE | FAULT/METAL_ROUTE_NOT_IMPLEMENTED, commands off, both counts 0; no reject implementation claimed |
| S2-17 | Enter ACCEPT with metal FALSE; then toggle metal TRUE and finish passage | Route remains ACCEPT; normal completion counts exactly once |
| S2-18 | Independent runs: both limits TRUE; both exits TRUE; lose home in FEED/ACCEPT; any exit in FEED; reject exit in ACCEPT. Also run modes 5 and 6 separately for reserved-state injection with a coincident Reset edge | LIMIT_CONFLICT, EXIT_CONFLICT, PUSHER_NOT_HOME or UNEXPECTED_EXIT as applicable; no movement/count. Modes 5/6: detection scan FAULT/INVALID_STATE/alarm=TRUE; held Reset cannot clear it; release and later new Reset gives READY/NONE with no movement |
| S2-19 | READY, block station then press Start. Clear path; set permissive FALSE and Stop TRUE | First fault START_NOT_CLEAR remains latched despite new conditions. Restore all, release Start/Stop, new Reset → READY |
| S2-20 | Retain the coverage captures below, including continuous manual FEED-timeout and ACCEPT-timeout recovery runs; after each recovery start a fresh FEED and observe its full timeout window | Entry ET=0; inactive timer ET=0/Q=FALSE by next scan after exit/timeout; Stop and Reset do not move or add counts; fresh Start enters FEED at ET=0 with a new measured 5 s window. Every coverage item needs its named capture |

Use one dedicated manual sequence for the nominal 1.8 s station-to-accept travel if
desired; manual tests and scripted tests do not validate the proposed mechanics.

## 4. Deterministic replay and deadline cases

Log out. Replace the task call with **only `PRG_TestSequence`**, rebuild and log in
to IDE simulation. Remove all forces. For **every case**, stop the application,
Reset Cold, write `PRG_TestSequence.testCase` while stopped, then Run. Do not change
the case during a run; changing case or Stop/Run without Reset Cold does not
restart its counter or controller. Observe `done`, `sequence_passed`, `failed`, `scan`,
`dut` and `samples`. These flags are outputs from the test, not evidence until run.
`sequence_passed` means only that the runner assertions matched; it never supplies
a measured timing verdict or automatically changes the result register.

The runner writes all ten inputs, calls its private DUT once per active scan and
stores the pre-call `entry_state` and post-call sample in `samples[scan]`. When done it freezes the array;
it is not a continuously executing process controller. Samples are bounded at
301 rows. Copy/export the used samples or capture the relevant rows and save the
actual observations. Restore `PLC_PRG` for subsequent manual tests.

| ID | testCase | Scripted stimulus / nominal scan | Required observations |
| --- | ---: | --- | --- |
| S2-21 | 0 | Reset 1, held Start 2, station 3, accepted high 4–5, both clear 6; Stop 9, Reset 10; fresh Start 12; finish 13 | sequence_passed=TRUE; one count at scan 6 and no repeat while Start held; Stop/Reset do not move; fresh FEED at 12 with feed_et=0 and count 1. No timeout recovery or full fresh-window proof in this mode |
| S2-22 | 1 | FEED enters 2; station arrives 252 (nominal 5000 ms); continue through 253 | At 252: previous FEED, new station input, FAULT/FEED_TIMEOUT with feed_q=TRUE and count 0. At 253: fault remains, feed_et=0/feed_q=FALSE. Measured boundary evidence required |
| S2-23 | 2 | ACCEPT enters 3; accepted high 4–152, clears 153 (nominal 3000 ms); continue through 154 | At 153: previous ACCEPT/count 0 and accepted high, new falling input, FAULT/ACCEPT_TIMEOUT with accept_q=TRUE and count 0. At 154: fault remains, accept_et=0/accept_q=FALSE. Measured boundary evidence required |
| S2-24 | 3 | Station arrives 251 (nominal FEED 4980 ms); accepted high 252, clear 253 | Scan 250 FEED/count 0/station FALSE; scan 251 station TRUE, ACCEPT/count 0/feed_q=FALSE/feed_et<5 s. Scan 252 ACCEPT/count 0; scan 253 READY/count 1. Timestamped deadline bracket required |
| S2-25 | 4 | ACCEPT enters 3; accepted high 4–151, clears 152 (nominal 2980 ms); continue through 153 | Scan 151 ACCEPT/count 0/accepted TRUE/accepted_seen TRUE; scan 152 accepted FALSE, READY/count 1/accept_q=FALSE/accept_et<3 s; scan 153 READY/count 1 with accept_et=0/accept_q=FALSE. Timestamped deadline bracket required |

Modes **5 and 6** belong to S2-18, not new result rows. On scan 1 they inject
EXTEND or RETRACT respectively before the DUT call, while supplying a Reset rising
edge, healthy permissive, clear cell and Start/Stop FALSE. Require
FAULT/INVALID_STATE and alarm TRUE on scans 1–3; Reset is held on scan 2, released
on scan 3, then raised again on scan 4. Only scan 4 may recover to READY/NONE;
scan 5 stays READY, count 0 and both movement commands FALSE. Retain scans 0–5,
including `entry_state`, inputs, fault and all four outputs for each mode.

### Required measured boundary evidence (S2-22–25)

Nominal scan numbers and `sequence_passed=TRUE` are **not timing evidence**.
Use an actual timestamped CODESYS task trace sampled on MainTask every cycle, or
validated timestamp instrumentation at the timer calls. Save phase-entry,
previous, completion and next-scan timestamps along with inputs, state, ET/Q,
outputs and count. Record the clock origin, units, resolution, sampling position
and any offset/uncertainty relative to the timer call. `scan * 20 ms` is not a
measured clock. The sample array deliberately contains no invented timestamps.

For same-scan timeout cases, the capture must show the completion input changing
in the actual scan where the active timer reports Q=TRUE, with the timeout fault
and no count. Keep the following scan showing ET=0/Q=FALSE while FAULT remains.
For each one-scan-early case establish, using the same clock and measured phase
entry `t_entry`, the bracket:

```text
t_previous < t_completion < t_entry + PT <= t_next
```

Use PT=5 s for FEED and PT=3 s for ACCEPT. The previous sample must show the
active phase with count 0; the completion sample must show the changed input and
correct transition/count with ET<PT and Q=FALSE. The next sample must be the
immediately following task execution, even though the exited phase timer has
reset. Mode 4 now retains scan 153 for that purpose. Do not infer the original
deadline from the reset timer's ET. If clock resolution, sampling offset, dropped
samples or jitter prevent establishing the bracket, record **INCONCLUSIVE** and
retain the capture. A definite sequence violation is **FAIL**; explain it
separately from an inconclusive timing comparison. Do not change the presets or
copy expected timestamps to obtain PASS. If the installed IDE/target cannot
capture suitable timestamps, the boundary tests remain INCONCLUSIVE or NOT RUN.

### S2-20 coverage and continuous recovery procedure

S2-21 covers only normal passage, held Start and Stop/Reset/fresh Start. It has no
fault or complete fresh 5 s window. Link each required observation to the actual
capture file and scan/time range in a run note:

| Coverage item | Required capture |
| --- | --- |
| FEED entry; FEED-to-ACCEPT entry; next-scan FEED reset | Mode 0 scans 2–4 |
| Confirmed passage; next-scan ACCEPT reset | Mode 0 scans 5–7 |
| Stop from READY; Reset without motion; fresh Start and FEED ET=0 | Mode 0 scans 9–13 |
| Stop during FEED and during ACCEPT; movement and timer reset; discarded passage memory | Both S2-11 runs, including the resumed ACCEPT and new passage |
| FEED timeout Q=TRUE, then Q=FALSE/ET=0 with fault still latched | Mode 1 scans 251–253, or corresponding continuous manual capture |
| ACCEPT timeout Q=TRUE, then Q=FALSE/ET=0 with fault still latched | Mode 2 scans 152–154, or corresponding continuous manual capture |
| Recovery after each timeout; new FEED with full 5 s window | Two continuous PLC_PRG traces using the sequence below; not mode 0 or frozen timeout samples |

For each of the **FEED timeout** and **ACCEPT timeout**, independently:

1. Cold-reset once and run `PLC_PRG` with one 20 ms task. Start a continuous trace
   before arming. Produce the selected timeout using S2-10 or S2-08. Preserve the
   timeout scan and at least the next two task calls: the fault stays latched,
   movement commands are FALSE and the expired timer resets to ET=0/Q=FALSE.
2. Without IDE Stop, Reset Cold, download or switching task entry, restore the
   healthy clear cell and release Start/Stop/Reset. Pulse operator Reset. Capture
   READY/NONE with conveyor=FALSE, extend=FALSE, alarm=FALSE, ready=TRUE and the
   unchanged count. Holding/resetting alone must not enter FEED.
3. Release Reset, ensure Start has been FALSE for a full task call, then apply a
   fresh Start edge. Capture FEED entry with feed_et=0/feed_q=FALSE. Keep station
   and both exit inputs FALSE, home TRUE, extended FALSE and permissive TRUE.
4. Continue the **same trace** until the new FEED timeout. Using actual task
   timestamps and ET/Q, establish a new 5 s interval from this FEED entry, rather
   than a leftover interval from the previous phase. Capture the last pre-timeout,
   timeout and next scans, including outputs and unchanged count. Record jitter
   and clock uncertainty; if the fresh interval cannot be established, S2-20 is
   INCONCLUSIVE. A missing run is NOT RUN.

Do not stitch a cold start onto a fault capture and call it recovery. The required
run note must map both continuous traces and the other rows above before S2-20
can be PASS. These are prepared instructions; no such capture is supplied yet.

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
