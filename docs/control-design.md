# Control design

## State and output contract

Outputs are derived from the resulting state at the end of each scan. Count changes occur only on successful cycle completion.

| State | Conveyor | Extend valve command | Normal transition |
| --- | ---: | ---: | --- |
| STOPPED | 0 | 0 | New Reset edge, clear path and pusher home → READY |
| READY | 0 | 0 | New Start edge and clear path → FEED |
| FEED | 1 | 0 | Station detects part; latch route → ACCEPT or EXTEND |
| ACCEPT | 1 | 0 | Accept sensor has gone true then false and station clear → increment accept, READY |
| EXTEND | 0 | 1 | Pusher extended feedback → RETRACT |
| RETRACT | 0 | 0 | Pusher home, reject passage complete and station clear → increment reject, READY |
| FAULT | 0 | 0 | Eligible Reset edge → READY; otherwise remain latched |

The proposed cylinder is spring-return. `extend=false` requests no extension; in a real pneumatic system this may cause retraction. Zero commands are not a universal "no physical motion" state.

## Scan order

1. Capture Start and Reset rising edges, even when the state cannot use them.
2. Check permissive and contradictory feedback; latch the first fault.
3. If faulted, allow only eligible reset and return with movement commands off.
4. Apply Stop before any normal transition; enter STOPPED.
5. Process STOPPED recovery or READY start. A reset and start cannot happen in one scan.
6. For active movement states, advance the phase timer and apply the timeout before accepting completion.
7. Check unexpected-route feedback and pusher home during conveyor movement.
8. Evaluate the current phase and derive outputs from the resulting state.

The timer is zero on state entry and advances on subsequent ticks. All Python timeouts must be positive integer multiples of the scan duration. At exactly the deadline, the transition is a fault even if feedback arrives on that tick. PLC timer implementation must explicitly preserve this boundary policy; compare measured transitions with the reference and document any scan-level offset.

## Why count passage rather than sensor activation?

A held-high exit sensor is not proof that a part has left the cell. The controller remembers that the expected exit was seen and waits for it to clear. It also requires the station to clear. A held signal therefore reaches a timeout instead of incrementing every scan. The single-part assumption makes a one-bit passage memory sufficient; a continuous conveyor would require part tracking and different logic.

## Faults and recovery

| Code | Trigger | Operator investigation in simulation |
| --- | --- | --- |
| INTERLOCK_OPEN | `permissive_ok=false` | Restore the simulated permissive; inspect/reset the interrupted cycle |
| LIMIT_CONFLICT | Home and extended both true | Correct contradictory cylinder feedback |
| EXIT_CONFLICT | Accept and reject sensors both true | Clear conflicting exit inputs |
| START_NOT_CLEAR | Start requested with an occupied path or non-home pusher | Remove the staged condition and return pusher home |
| PUSHER_NOT_HOME | Home feedback lost in FEED or ACCEPT | Check the pusher status before allowing belt motion |
| UNEXPECTED_EXIT | Exit in FEED or exit on the wrong selected route | Inspect sensor sequence / misrouting |
| FEED_TIMEOUT | Station not reached before 5.0 s | Missing part, stopped belt or station signal failure |
| ACCEPT_TIMEOUT | Confirmed accept passage not complete before 3.0 s | Obstruction or accept/station signal failure |
| EXTEND_TIMEOUT | Extended limit absent before 1.0 s | Cylinder or extended feedback failure |
| RETRACT_TIMEOUT | Home or complete reject passage missing before 1.0 s | Cylinder return, chute blockage or reject/station signal failure |

The messages suggest investigations; they do not diagnose a physical cause from one bit.

For interrupted cycles, this MVP deliberately discards the in-process part record. In simulation, clear the part/sensor inputs and restore home feedback, release Start and Stop, press and release Reset, then press Start for a new part. Completed counters remain; an interrupted cycle is not counted. Resetting the Python process represents a new session and clears counts.

## Decisions and limitations

| Decision | Benefit | Limitation / later extension |
| --- | --- | --- |
| Manual feed, one Start per part | Makes part identity and count reasoning inspectable | Does not detect an unsensed second part or prove throughput |
| Symbolic inputs, no device addresses | Same behavior can be replayed in multiple tools | Real I/O polarity and wiring still need commissioning |
| Scripted sensor inputs in Python | Small, deterministic and easy to test | No friction, dynamics, continuous plant or PLC connection |
| Feedback-driven pusher sequence | Missing motion completion is observable | Two limit switches still cannot prove a safe physical state |
| Latched fault with clear-cell recovery | Avoids uncertain mid-cycle restart | Interrupted work needs operator intervention |
| Textbook IDE simulation for the PLC port | No hardware required | Does not establish real-time performance or hardware reliability |

## Future extensions, only after the MVP

Add a simple 1D moving-part model, timing variability and sensor debounce; validate it separately. Add a feeder/entry sensor before attempting automatic repeat. Multiple-part tracking, communications and real hardware each need their own requirements and tests.
