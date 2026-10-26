# Requirements and acceptance criteria

## Design basis

This is a manually fed, one-part-per-cycle sorting cell. A metal part takes the reject route; a non-metal part takes the straight accept route. "Reject" identifies a route, not an inferred product defect. A real material specification and sensor selection would need a separate design review.

The starter assumes that Boolean inputs are already debounced and that the classification sensor is valid when the station photoeye first becomes true. It does not model sensor reliability, belt inertia, friction, air pressure or electrical noise. A false-negative material sensor can misroute a part; this design has no redundant classification check.

| ID | Requirement | Observable acceptance criterion |
| --- | --- | --- |
| R01 | Deliberate startup | Power-up is STOPPED. Reset with a clear cell leads to READY without motion. Start alone cannot bypass reset. |
| R02 | One part per cycle | Only a new Start rising edge in READY begins FEED; holding Start cannot repeat the cycle. Manual feeding must enforce one-part occupancy. |
| R03 | Stable route selection | At the station, `metal=false` selects ACCEPT and `metal=true` selects EXTEND. Later material-sensor changes do not change the route. |
| R04 | Confirmed accept count | The accept sensor must be seen true and subsequently false, with station clear, before exactly one accept is counted. |
| R05 | Confirmed reject count | Extended feedback must be seen first; return to home, reject passage true then false, and clear station are required before exactly one reject is counted. |
| R06 | Exclusive movement commands | Conveyor and pusher extend commands must never both be true in the same scan. |
| R07 | Bounded waits | FEED, ACCEPT, EXTEND and RETRACT each fault at their configured deadline if not already complete. Timeout wins over same-scan success. |
| R08 | Stop and permissive response | Stop suppresses both movement commands in the evaluated scan. A false permissive suppresses commands and latches a fault. No automatic restart follows. |
| R09 | Controlled reset | Fault reset needs a new Reset edge, healthy permissive, clear path, pusher home, and Start/Stop released. Reset cannot itself move the cell. |
| R10 | Plausibility checks | Conflicting cylinder limits, conflicting exit sensors, a wrong-route exit, or home feedback lost during conveyor movement must fault. |
| R11 | Stable diagnostics | Preserve the first fault until valid reset. Stop must not erase an existing fault. Completed counts survive Stop/Reset within a session. |
| R12 | Reproducible evidence | A fresh checkout can run all reference tests; demos produce CSVs of inputs, state, outputs, counts and fault. |

## Timing assumptions — proposed values, not measurements

| Quantity | Initial assumption | Reasoning / change gate |
| --- | --- | --- |
| Logical scan | 20 ms | Deterministic reference step; later measure PLC task behavior |
| Part | 30 mm diameter, 10 mm high puck | Simplifies layout and avoids irregular-part handling |
| Belt nominal speed | 100 mm/s | Proposed low-speed model value |
| Staging-to-station travel | 300 mm | Nominal travel 3.0 s; FEED timeout 5.0 s gives 2.0 s allowance |
| Station-to-accept sensor | 180 mm | Leading-edge travel 1.8 s plus about 0.3 s for the part to clear; ACCEPT timeout 3.0 s |
| Pusher stroke / nominal speed | 100 mm / 200 mm/s | Nominal 0.5 s each direction; 1.0 s limit per extend/retract phase |
| Ideal photoeye pulse | 30 / 100 = 0.30 s | About 15 scans at 20 ms, before accounting for the optical field |

These calculations motivate starting timeout values. The scripted demo inputs deliberately execute faster and **do not validate these mechanical assumptions**. Recalculate and retest after changing geometry, scan interval, actuator assumptions or any real device.

## Release definition

The Python starter is complete when its tests and four example scenarios pass with recorded results. The planned **portfolio MVP** is complete only when the PLC compiles, the required scenarios are replayed in CODESYS, operator controls work, the CAD deliverables exist and the evidence describes what was actually tested. CAM is optional and cannot block the core automation release.

A physical build is a separate project. The simulated permissive is not an emergency-stop implementation. There is no safety performance level, SIL, compliance or commissioning claim.
