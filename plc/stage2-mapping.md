# Stage 2 mapping and execution contract

Status: source implemented; CODESYS compilation and runtime behavior unverified.
The canonical process symbols remain in [io-map.csv](../docs/io-map.csv).
No absolute addresses, physical channels, fieldbus configuration or persistent variables are assigned.

## I/O binding

`PLC_PRG.simInputs` is passed by value to `PLC_PRG.sorter.i` once per task.
The test program instead owns `PRG_TestSequence.simInputs` and its own `sorter`.
Schedule only one of these programs. Never write controller state, output, counter or timer internals to make a functional test pass.

| Canonical symbol | Manual watch path | Type / initial value | Stage 2 use |
| --- | --- | --- | --- |
| start | `PLC_PRG.simInputs.start` | BOOL / FALSE | R_TRIG every call; accepted only in READY with Reset low |
| reset | `PLC_PRG.simInputs.reset` | BOOL / FALSE | Separate R_TRIG every call; eligible STOPPED/FAULT recovery only |
| stop | `PLC_PRG.simInputs.stop` | BOOL / FALSE | Level; suppresses movement and enters STOPPED unless already faulted |
| permissive_ok | `PLC_PRG.simInputs.permissive_ok` | BOOL / TRUE | False latches INTERLOCK_OPEN |
| station | `PLC_PRG.simInputs.station` | BOOL / FALSE | FEED classification trigger; must clear before counting |
| metal | `PLC_PRG.simInputs.metal` | BOOL / FALSE | Read on first FEED station detection only; true faults as unsupported |
| accepted | `PLC_PRG.simInputs.accepted` | BOOL / FALSE | Must be sampled true in ACCEPT, then false with station clear |
| rejected | `PLC_PRG.simInputs.rejected` | BOOL / FALSE | Included in clear-path and unexpected-exit guards; no reject sequence |
| pusher_home | `PLC_PRG.simInputs.pusher_home` | BOOL / TRUE | Required for reset/start and throughout conveyor motion |
| pusher_extended | `PLC_PRG.simInputs.pusher_extended` | BOOL / FALSE | Clear-path and contradictory-limit checks only |
| conveyor | `PLC_PRG.sorter.o.conveyor` | BOOL / FALSE | True only in resulting FEED or ACCEPT state |
| extend | `PLC_PRG.sorter.o.extend` | BOOL / FALSE | Always false in Stage 2 |
| alarm | `PLC_PRG.sorter.o.alarm` | BOOL / FALSE | True in resulting FAULT state |
| ready | `PLC_PRG.sorter.o.ready` | BOOL / FALSE | READY and clear path/home; does not start motion |

## State codes

| Code / enum | Movement outputs (conveyor, extend) | Transitions |
| --- | --- | --- |
| 0 / STOPPED | 0, 0 | Eligible Reset edge → READY |
| 1 / READY | 0, 0 | Start edge with Reset low and clear path → FEED; blocked path → FAULT |
| 2 / FEED | 1, 0 | Station and non-metal → ACCEPT; deadline / invalid feedback / metal → FAULT |
| 3 / ACCEPT | 1, 0 | Seen accept true, now false, station clear before deadline → count once, READY |
| 4 / EXTEND | Not implemented | Reserved; if encountered, INVALID_STATE → FAULT |
| 5 / RETRACT | Not implemented | Reserved; if encountered, INVALID_STATE → FAULT |
| 6 / FAULT | 0, 0 | Eligible Reset edge → READY; Stop preserves fault |

Codes are explicit PLC mappings; the Python reference uses string states. Stage 3 may reuse 4/5 but is not delivered here.

## Diagnostics

| Code | Enum | Condition |
| --- | --- | --- |
| 0 | NONE | No latched fault |
| 1 | INTERLOCK_OPEN | Permissive false |
| 2 | LIMIT_CONFLICT | Home and extended both true |
| 3 | EXIT_CONFLICT | Accept and reject both true |
| 4 | START_NOT_CLEAR | Eligible Start with occupied path or pusher not home |
| 5 | PUSHER_NOT_HOME | Home lost in FEED/ACCEPT |
| 6 | UNEXPECTED_EXIT | Any exit in FEED; reject exit in ACCEPT |
| 7 | FEED_TIMEOUT | FEED TON reaches 5 s |
| 8 | ACCEPT_TIMEOUT | ACCEPT TON reaches 3 s |
| 9 | METAL_ROUTE_NOT_IMPLEMENTED | Metal detected at FEED station trigger |
| 10 | INVALID_STATE | Reserved/unhandled state encountered |

The first fault persists until eligible Reset. Eligibility: fresh Reset edge, Start and Stop low, permissive healthy, all three path sensors low, home true, extended false. Reset does not clear completed counts. An aborted passage is discarded. Reset during FEED/ACCEPT is consumed and ignored; it is not a stop command. In READY, simultaneous Start/Reset is ignored and a new Start edge is required after release. This last rule is deliberately stricter than the current Python reference, which does not inhibit Start with Reset in READY.

## Scan and timer contract

1. Capture both edges, including in states where they are ignored. Calculate clear path.
2. Call both TONs with the current state, then capture their Q values into `xFeedDeadline` / `xAcceptDeadline` for this scan.
3. Default outputs off. Check global faults; keep any previously latched fault.
4. Process eligible fault reset; otherwise Stop; otherwise exactly one current-state branch. Reset and Start cannot advance two states in one call.
5. In active states check timeout before home/route checks and normal completion. Same-scan completion loses whenever the relevant TON.Q is true.
6. On state change only, call both TONs again using the new state: the departing timer resets and the arriving timer starts in the transition scan. Clear passage memory. This intentional second call avoids delaying the timer origin by one cyclic scan.
7. Publish final ET values and derive outputs from the resulting state.

At FEED/ACCEPT entry, ET is expected to be T#0ms; after exit, both inactive timers must report ET=0 and Q=false. `xFeedDeadline`/`xAcceptDeadline` and `tFeedDecisionElapsed`/`tAcceptDecisionElapsed` capture Q/ET before transitions reset the timers. A timeout scan can therefore show a deadline snapshot true even though the reset timer's final ET is zero. Inspect the decision snapshots when verifying deadline priority and the final ET fields when verifying reset. TON ET may saturate at PT; PT alone does not prove zero lateness in wall-clock time.

Timers use Standard-library elapsed time, not `scan_count * 20 ms`. In an ideal 20 ms task, FEED reaches 5 s on the 250th scan after entry and ACCEPT reaches 3 s on the 150th. The IDE is not a real-time scheduler: record actual ET and task timing. A nominal scan-249 arrival can be late if the task is delayed. Do not declare an exact-boundary pass using a stopwatch or a watch-window refresh. If runtime TON behavior differs from the stated entry/reset contract, retain the discrepancy and fix/retest before closing the gate.

## Lifetime and limits

All application variables are non-retained. A new initialized instance starts STOPPED, count 0, outputs false. Operator Stop/Reset preserves count; CODESYS Reset Origin/new download is a separate lifecycle operation and initializes it. Do not claim behavior across warm restarts or online changes until separately checked. The count is UDINT; overflow behavior is outside this one-part gate.

This source handles only one manually staged non-metal part per Start. Sensor debounce, short pulses missed between scans, mechanical motion, reject operation, full Stage 3 fault coverage and hardware safety are not verified. A post-selection metal change in ACCEPT does not change the route. Guards included here support the accept sequence; they do not complete Stage 3 or R01–R12 verification.
