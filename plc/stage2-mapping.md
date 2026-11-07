# Stage 2 PLC design and mapping

**Source implementation supplied; CODESYS compilation and execution not yet verified.**
The full-cell contract remains in `docs/control-design.md`. This document defines
the smaller Stage 2 port and its explicit differences from the Python reference.

## Objects and task

All readable ST files are in [exports](exports/). They are authored source, **not
exports obtained from a compiled IDE project**. Create five DUTs (two enums, input,
output and trace structures), two PROGRAM POUs and one FUNCTION_BLOCK
POU as described in [the simulation procedure](stage2-simulation.md).

Use one cyclic task, `MainTask`, interval **T#20ms**, with exactly one call:
`PLC_PRG` for manual tests or `PRG_TestSequence` for deterministic replay. Both own
independent controller instances; never schedule both for a single test. The only
library dependency in the sources is Standard (`R_TRIG`, `TON`). No device addresses,
GVL, HMI, Python connection, I/O driver or persistent variables are required.

## I/O and initialization

[stage2-io-map.csv](stage2-io-map.csv) maps every existing repository symbol to its
manual watch path, type, initial value and Stage 2 use. The reference names and
polarities in [docs/io-map.csv](../docs/io-map.csv) are unchanged. The test runner
uses `PRG_TestSequence.inputs.<symbol>` and `PRG_TestSequence.dut.o.<symbol>` instead.
These are simulation variables, **not electrical addresses**.

Inputs initialize to FALSE except `permissive_ok=TRUE` and `pusher_home=TRUE`.
State initializes to STOPPED, fault to NONE, counts to zero, passage memory to
FALSE and commands to FALSE. All instance data is non-retained. An IDE Reset Cold
reinitializes it; an operator Reset input preserves completed counts. IDE Stop/Run
alone is not a cold startup and can resume instance state. Use Reset Cold for each
independent test; a real controller restart policy is outside this package.

## State mapping and transitions

The Python enum uses strings. Numeric PLC values are explicitly assigned for
stable watch/HMI display; they are not Python ordinal values.

| PLC state | Code | Conveyor | Extend | Transition / count |
| --- | ---: | ---: | ---: | --- |
| STOPPED | 0 | 0 | 0 | Eligible new Reset edge → READY |
| READY | 1 | 0 | 0 | New Start edge, Reset released and clear path → FEED |
| FEED | 2 | 1 | 0 | Station=TRUE, metal=FALSE → ACCEPT; metal=TRUE → FAULT |
| ACCEPT | 3 | 1 | 0 | Seen accepted=TRUE, then accepted=FALSE and station=FALSE → count +1 and READY |
| EXTEND | 4 | — | — | Reserved; entering it trips INVALID_STATE |
| RETRACT | 5 | — | — | Reserved; entering it trips INVALID_STATE |
| FAULT | 6 | 0 | 0 | Scan began in FAULT and eligible new Reset edge → READY; first fault stays latched otherwise |

`ready` means READY **and** clear path. `alarm` means FAULT. `extend` is always
FALSE, `rejected_count` always zero. A clear path means station, both exits and
extended feedback FALSE, with home TRUE. Reset eligibility also requires healthy
permissive and Start/Stop released. A denied Reset edge is consumed: clearing the
obstruction while holding Reset does not retry it. A Start edge outside READY is
consumed. No queued starts and no automatic repeat are implemented.

A fault detected on the current scan cannot be reset on that same scan, even if
a Reset edge coincides with an invalid/reserved state. The edge is consumed;
recovery needs a later release/repress while the scan begins in FAULT. Runner
modes 5/6 prepare a defensive check for EXTEND/RETRACT respectively.

Reset while moving is ignored; use Stop to interrupt. In READY, asserted Reset
inhibits a concurrent Start edge. This is a deliberate stricter policy than the
current Python READY branch, which does not check Reset. The simultaneous edge is
consumed and must be released/repressed. The documented “Reset cannot start motion”
intent takes priority here; do not claim full behavioral equivalence to Python.

## Scan order and timers

1. Save state at scan entry. Call both edge detectors unconditionally.
2. Check permissive, conflicting limits/exits and invalid state, preserving any
   already latched fault. Only a scan that **began in FAULT** can handle an
   eligible fault reset; a newly detected fault stays visible. Otherwise handle Stop or
   STOPPED recovery or READY start. A recovery branch cannot also process Start.
3. Call FEED TON with the current FEED condition, including the entry scan.
   Only if the scan **began** in FEED, evaluate timeout first, then home/exit
   plausibility, then station classification.
4. Call ACCEPT TON with the current ACCEPT condition, including the FEED→ACCEPT
   entry scan. Only if the scan **began** in ACCEPT, evaluate timeout first, then
   home/wrong-exit checks, then passage and count.
5. Clear passage memory outside ACCEPT. Copy timer diagnostics and derive all
   outputs from the final state. Stop/fault therefore removes commands this scan.

FEED preset is **5 s**; ACCEPT preset is **3 s**. Both TONs are called exactly once
each scan. Ordering their calls around the transitions starts each timer on its
state's entry scan, with expected ET=0, avoiding a planned one-scan start delay.
`scanState` prevents processing both movement phases on one scan.

The timer for a phase that exits during its own logic still reports its last ET/Q
for that scan, then resets to ET=0/Q=FALSE on the next scan. For example, FEED→ACCEPT
reports FEED's last ET and ACCEPT ET=0. An ACCEPT timeout reports accept_q=TRUE on
the FAULT transition scan and FALSE on the next scan. This intentional diagnostic
lag differs from Python's `elapsed_ms`, which resets immediately on every state
transition. Never compare those fields without accounting for this difference.

With an ideal 20 ms task, entry at scan k means ET=(n−k)*20 ms until expiry;
FEED expires at k+250, ACCEPT at k+150. In the actual IDE, TON uses elapsed time,
not a Python tick count. Jitter may change the expiry scan. **Q=TRUE wins over
completion on the same evaluated scan**, even when accepted clears or station
arrives. Record actual ET/Q and task jitter; do not infer a measured 20 ms response
from the configured interval. No CODESYS timing equivalence has yet been measured.

The earlier guards have priority over phase timeout: global faults > Stop > phase
timeout > movement plausibility > normal phase completion. While already faulted,
Stop never overwrites the first fault. Counts survive Stop/Reset; incomplete passage
memory does not. A maximum UDINT count faults rather than wrapping.

## Fault mapping

| Code | Enum | Trigger / Stage 2 role |
| ---: | --- | --- |
| 0 | NONE | No latched fault |
| 1 | INTERLOCK_OPEN | Simulated permissive FALSE |
| 2 | LIMIT_CONFLICT | Home and extended both TRUE |
| 3 | EXIT_CONFLICT | Both exit sensors TRUE |
| 4 | START_NOT_CLEAR | Eligible Start in READY with occupied path / non-home pusher |
| 5 | PUSHER_NOT_HOME | Home lost in FEED/ACCEPT |
| 6 | UNEXPECTED_EXIT | Any exit in FEED; reject exit in ACCEPT |
| 7 | FEED_TIMEOUT | FEED TON Q TRUE |
| 8 | ACCEPT_TIMEOUT | ACCEPT TON Q TRUE |
| 9 | METAL_ROUTE_NOT_IMPLEMENTED | Metal detected at station; stops instead of misrouting |
| 10 | INVALID_STATE | Reserved/unrecognized state supplied to this Stage 2 instance |
| 11 | COUNT_OVERFLOW | Confirmed passage with accepted count already at UDINT maximum |

These supporting guards let the partial sequence stop deliberately; they do not
complete Stage 3. EXTEND/RETRACT, reject counting/timers, full fault-matrix replay,
HMI, native project/archive, CAD and hardware commissioning remain outstanding.
