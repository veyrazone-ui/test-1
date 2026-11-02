# CODESYS IDE simulation: Stage 2 procedure and expected results

**All CODESYS outcomes below are EXPECTED, NOT RUN.** Record observations in [stage2-results.csv](../evidence/stage2/stage2-results.csv). A Python test pass or source review is not a PLC build or simulation result.

## Build the project

1. Use CODESYS Development System V3.5. Record exact service pack/patch, compiler version, device description, OS and resolved Standard library version. This package has not established a tested version baseline.
2. File → New Project → Standard project; choose an installed CODESYS device supporting IDE simulation and ST for PLC_PRG. Save as `plc/ConveyorSorting.project`. Use no physical I/O mapping. There is no `.project` in this package yet.
3. Under Application, add DUT objects named `E_CellState`, `E_CellFault`, `ST_CellInputs`, `ST_CellOutputs`, and `ST_Stage2Sample`. Replace their declaration contents with the corresponding complete `.st` files in `exports/`, including attributes and TYPE/END_TYPE.
4. Add `FB_ConveyorSorter` as a Function Block in ST and `PRG_TestSequence` as a Program in ST. Use the generated `PLC_PRG` Program for the manual wrapper. For these three POUs, paste the source from its opening FUNCTION_BLOCK/PROGRAM line through the final END_VAR into the declaration pane. Paste the code after the `// IMPLEMENTATION` marker into the implementation pane, **excluding** the terminal END_FUNCTION_BLOCK/END_PROGRAM. The `.st` files are readable source listings, not native CODESYS import files or compiler-generated exports. Do not use File → Import expecting raw `.st` to reconstruct the project.
5. In Library Manager, resolve the Standard library containing TON and R_TRIG. Confirm the types resolve; do not substitute unrelated vendor timers without reviewing the timing contract.
6. Under Task Configuration, set MainTask to **Cyclic**, interval **T#20ms**, and one call: `PLC_PRG`. Remove other application calls. Record task priority and watchdog settings; do not assume they prove real-time performance. There must be exactly one sorter invocation per cyclic task.
7. Build → Rebuild. Save the full messages log and record errors and warnings. Required result: zero errors; inspect every warning. Fix and re-run before claiming compilation. Capture a task-configuration screenshot.
8. While logged out, select Online → Simulation, then Online → Login and accept creation/download of the simulated application. Confirm the IDE indicates simulation. Start with Debug → Start. No gateway connection to a real PLC is required for this procedure.
9. Use Reset Origin/re-download when a fresh test instance is requested; record which operation was used. This is distinct from the application input `simInputs.reset`. Clear all forcing and prepared values before each test.

## Watch and trace setup

Add all fields of `PLC_PRG.simInputs`, `PLC_PRG.sorter.o`, `eState`, `eFault`, `udiAcceptedCount`, `xAcceptedSeen`, `xStartEdge`, `xResetEdge`, `tFeedElapsed`, `tAcceptElapsed`, `tFeedDecisionElapsed`, `tAcceptDecisionElapsed`, `xFeedDeadline` and `xAcceptDeadline`. For automatic runs use the same paths under `PRG_TestSequence` and also watch `xRun`, `xDone`, `xFailed`, `udiScan` and `samples`. Decision ET fields preserve elapsed values from before the state transition; final ET fields show the reset/new timer.

Use a task-sampled CODESYS Trace, if supported, to capture state, count, station/accepted, both ETs, both deadline snapshots and conveyor each MainTask call. If unavailable, the test driver's `samples` array stores scan-by-scan snapshots for automatic cases; save inspected values/export or screenshots and identify their scan indexes. The ordinary watch refresh is too slow to prove a one-scan edge or exact deadline. Never change state or timer internals to manufacture a pass.

Use **Write Values** for manually staged Boolean inputs and hold each condition across multiple scans (e.g. 100 ms or more). If forcing is used, remove it deliberately before a sequenced run: a persistent force can overwrite the driver's stimuli. Do not pause, single-step, use breakpoints or change task settings during timer measurement. TON elapsed time and task scan count are different observations.

## Manual first-count walkthrough (S2-01 through S2-05)

Start with all defaults from [mapping](stage2-mapping.md): clear station/exits, non-metal, permissive/home true, extended false, buttons low.

| Step | Write / observation | Expected state; count; movement |
| --- | --- | --- |
| A | Fresh initialized instance; run several scans | STOPPED; 0; conveyor=extend=false |
| B | Start true while STOPPED, hold | STOPPED; 0; no motion |
| C | Start false, then Reset true | READY; 0; no motion, ready=true |
| D | Keep Reset true; no other change | READY; 0; one Reset edge only |
| E | Reset false; then Start true and keep high through the cycle | FEED; 0; conveyor=true, extend=false; FEED ET starts at 0 |
| F | Before 5 s, set station=true with metal=false | ACCEPT; 0; conveyor=true; FEED ET=0, ACCEPT ET starts at 0 |
| G | Before 3 s, set accepted=true; hold briefly | ACCEPT; 0; xAcceptedSeen=true |
| H | Set accepted=false while station remains true | ACCEPT; 0; no count until station clears |
| I | Before 3 s total in ACCEPT, set station=false | READY; exactly 1; movement off; both timers reset |
| J | Keep Start high; toggle accepted true/false while READY, then clear | READY; still 1; no repeated cycle/count |
| K | Release Start; new Start edge | FEED; still 1; fresh FEED ET; next part needs a new passage |

Do not count a live run as successful merely because a sensor became true. Save evidence of G, H and I. Step K is optional for the one-count recording but required for S2-05 rearming; stop the new cycle without presenting another part.

## Test matrix

For each row record actual result, pass/fail/blocked, version, source revision and evidence path. Unless specified otherwise, use a fresh initialized instance and the Reset/Start setup above. "Outputs off" means conveyor and extend false; alarm may be true.

| ID | Stimulus | Expected result |
| --- | --- | --- |
| S2-00 | Assemble project, Rebuild, inspect MainTask | Zero compile errors; warnings reviewed; one call at 20 ms; native project/archive saved |
| S2-01 | Startup; Start held before Reset; release Start; valid Reset | STOPPED until Reset; READY without motion; count 0 |
| S2-02 | Reset with station/accepted/rejected occupied, no home, extended feedback, Start high or Stop high; then clear conditions while Reset remains high | No recovery/motion; relevant global faults may latch; a new eligible Reset edge is required |
| S2-03 | Simultaneous Start+Reset in STOPPED and READY; release Reset while Start stays high | No motion; fresh Start after releasing both is required in READY |
| S2-04 | Normal G→H→I true/false passage with station interlock | Exactly one count only at I; READY and outputs off; later metal changes in ACCEPT do not reroute |
| S2-05 | Hold Start through completion; pulse Start during ACCEPT; new Start only after READY | No queued/repeated start; edge in active state consumed; a new edge in READY starts FEED |
| S2-06 | Leave station false in FEED | At TON.Q, FEED_TIMEOUT, FAULT, no count, outputs off |
| S2-07 | In ACCEPT keep accepted true beyond 3 s | No count while held; ACCEPT_TIMEOUT, outputs off |
| S2-08 | In ACCEPT never assert accepted; station clear | No count; ACCEPT_TIMEOUT |
| S2-09 | Accept true then false but station held true | No count; ACCEPT_TIMEOUT if station never clears |
| S2-10 | Observe entry, exit, fault and restart ET/Q for both TONs | Entry ET=0; inactive timers ET=0/Q=false; FEED time does not carry into ACCEPT or next cycle |
| S2-11 | Station arrives at FEED elapsed 4980 ms and 5000 ms on separate runs | Before deadline → ACCEPT; at deadline/Q=true → FEED_TIMEOUT; log actual ET/scan timing |
| S2-12 | Seen accept true; final false with station clear at ACCEPT 2980 ms and 3000 ms on separate runs | Before deadline → count 1, READY; at deadline/Q=true → count 0, ACCEPT_TIMEOUT |
| S2-13 | Operational Stop in FEED and ACCEPT, including with passage completion | Same evaluated scan outputs off, STOPPED, no interrupted count; clear/release then fresh Reset and Start |
| S2-14 | Reset during FEED/ACCEPT; hold until a fault, then restore conditions | Reset does not restart or clear an active cycle; consumed edge cannot later reset fault; new eligible edge required |
| S2-15 | Lose permissive, home, or assert wrong exit during each active state; also test contradictory limits/exits | Corresponding latched fault; outputs off; clear input alone does not restart; Stop preserves first fault |
| S2-16 | Complete one count, Stop, Reset; abort another seen-high passage and reset | Count stays 1 through operator actions; aborted passage never counts and memory is cleared |
| S2-17 | Station true with metal=true in FEED | METAL_ROUTE_NOT_IMPLEMENTED, count 0, both movement outputs off; no reject operation |
| S2-18 | READY with occupied path; new Start (Reset low) | START_NOT_CLEAR, outputs off, no count |

Rows with multiple conditions need separate sub-run records. S2-15 checks only the guards in this source; it does not claim the full Stage 3 fault/reject matrix. S2-11/12 need fresh fixtures for both sides of the deadline. Physical commissioning remains outside every row.

## Repeatable automatic stimulus driver

For repeatable sequences, log out and replace the MainTask call with **PRG_TestSequence only**. Set `uiScenario` and `uiArrivalScan` declaration initializers offline, rebuild, reset origin/re-download, then start the task and write `xRun=TRUE`. No manual input writes/forces during the run. `xDone` freezes the final sample index, and the following scan commands Stop. Judge the stored samples/trace, not the later live STOPPED state. A latched fault remains FAULT after that Stop. Reset Origin is required between runs; toggling xRun does not reset the test.

| uiScenario | uiArrivalScan | Expected frozen evidence |
| --- | --- | --- |
| 0 | ignored | Scan 0/1 STOPPED; 2/3 READY; 4 FEED; 10 ACCEPT; 11–15 seen-high/count0; 16–17 accepted low but station high/count0; 18 READY/count1; through 40 no repeat; xFailed=false |
| 1 | ignored | FEED_TIMEOUT by scan 400; count0; nominal deadline scan 254 |
| 2 | ignored | ACCEPT_TIMEOUT by scan 400; held accepted never counts; nominal deadline scan 160 |
| 3 | ignored | ACCEPT_TIMEOUT by scan 400; never-seen accept never counts |
| 4 | ignored | ACCEPT_TIMEOUT by scan 400; station prevents counting |
| 5 | ignored | Scan 10 FAULT/METAL_ROUTE_NOT_IMPLEMENTED; count0; extend=false |
| 6 | 249 then 250 | Station at 249/250 scans after FEED entry (4); expected before/at results in S2-11 |
| 7 | 149 then 150 | Accept falls at 149/150 scans after ACCEPT entry (10); expected before/at results in S2-12 |

`xFailed` checks several invariants and the normal-cycle count/state, not all matrix outcomes. False is not sufficient to pass the fixture: inspect expected fault, count, transitions and timing. Driver source is also **uncompiled and unrun** in this package.

For boundary runs inspect the relevant decision snapshot on the arrival scan. If IDE jitter means the nominal scan arrival was not actually before/at the timeout, record that run as inconclusive for the intended timing point, retain the trace, and repeat. Do not force TON.Q or edit internal state to get the desired result. Do not replace measured timing with the ideal scan numbers above.

## Evidence and completion gate

Save `.project`, `.projectarchive` with dependencies, readable exported source or PLCopen XML, build messages, task screenshot, normal-cycle trace, both timeout traces and before/at boundary traces. Fill every Stage 2 result row with actual observations and artifact links. A video is optional; invented screenshots or traces are not evidence.

Stage 2 is complete only after zero build errors and the startup/Reset/Start/confirmed-count/timer tests pass in IDE simulation. Any unexplained offset, warning or failure remains open. Full R01–R12 testing, reject operation, HMI, CAD and physical commissioning are separate later gates.

## Official references

- [Configuring a cyclic task](https://content.helpme-codesys.com/en/CODESYS%20Development%20System/_cds_creating_task_configuration.html)
- [Testing in simulation mode](https://content.helpme-codesys.com/en/CODESYS%20Development%20System/_cds_testing_in_simulation_mode.html)
- [Simulation limitations](https://content.helpme-codesys.com/en/CODESYS%20Development%20System/_cds_cmd_simulation.html)
- [Standard TON semantics](https://content.helpme-codesys.com/en/libs/Standard/3.5.15.0/Timer/TON.html)
- [Standard R_TRIG](https://content.helpme-codesys.com/de/libs/Standard/3.5.18.0/Trigger/R_TRIG.html)

The library documentation version is a reference, not an assertion about the user's installed library. Consulted 2 November 2026.
