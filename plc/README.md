# Stage 2 PLC source package

**Implemented in source; not compiled or run in CODESYS. Stage 2 gate remains open.** No native `.project`, `.projectarchive`, compiler-generated export, build success or measured PLC trace is claimed. The Python controller remains a separate behavioral reference.

The delivered ST sequence is **STOPPED → READY → FEED → ACCEPT → READY**. An eligible Reset establishes READY without motion; a fresh Start edge starts one manually staged non-metal part. The accept sensor must be sampled true and then false, with the station clear, before exactly one count. Holding Start cannot repeat the cycle. FEED and ACCEPT have separate 5 s and 3 s TONs with timeout priority over same-scan success.

## Package contents

| File | Purpose |
| --- | --- |
| [E_CellState.st](exports/E_CellState.st) | Explicit state codes; reject states reserved |
| [E_CellFault.st](exports/E_CellFault.st) | Guard/timeout fault codes for this subset |
| [ST_CellInputs.st](exports/ST_CellInputs.st), [ST_CellOutputs.st](exports/ST_CellOutputs.st) | Symbols and defaults matching the canonical I/O map |
| [FB_ConveyorSorter.st](exports/FB_ConveyorSorter.st) | Controller, edge detectors, timers, passage memory and count |
| [PLC_PRG.st](exports/PLC_PRG.st) | Manual simulation inputs; one controller call |
| [ST_Stage2Sample.st](exports/ST_Stage2Sample.st), [PRG_TestSequence.st](exports/PRG_TestSequence.st) | Simulation-only stimuli, invariant checks and scan snapshots; unrun |
| [stage2-mapping.md](stage2-mapping.md) | I/O paths, states, fault codes, scan order and known differences |
| [stage2-simulation.md](stage2-simulation.md) | Exact IDE assembly, 20 ms task setup, tests and expected outcomes |
| [Stage 2 evidence](../evidence/stage2/README.md) | Honest status, actual local checks, pending CODESYS results |

These `.st` files are hand-authored readable source listings in the planned `exports/` directory, not output from a CODESYS export. Follow the declaration/implementation paste instructions in the simulation procedure. The task interval is an IDE configuration step, not encoded in these listings.

## Scope and behavior

- Independent R_TRIG instances run on every call; unused edges are consumed.
- Reset in STOPPED/FAULT requires a clear path, home, healthy permissive and Start/Stop released. It preserves completed counts. In READY, Reset inhibits Start. Reset during motion is ignored, not used as Stop.
- A passage latch is cleared on every state change. Only ACCEPT can increment the count, and counting immediately leaves ACCEPT.
- Global input guards, operational Stop, first-fault latching and timeout recovery support this limited route. They do not complete Stage 3 verification.
- Outputs derive from the final state. Extend is always false. Metal at station triggers `METAL_ROUTE_NOT_IMPLEMENTED`; no reject count or pusher motion is implemented.
- No retention, physical I/O mapping, runtime connection to Python or hardware commissioning is included.

## Next step: reproduce in IDE simulation

Follow [the procedure](stage2-simulation.md). Use one 20 ms cyclic task with **either PLC_PRG or PRG_TestSequence**, never both. Record build messages, versions, task settings, actual test outcomes and traces before claiming the gate passed. Save the native project and dependency archive only after creating them in CODESYS.

The eventual full-port completion gate still requires the [full test matrix](../docs/test-plan.md), reject operation, fault/recovery tests and recorded R01–R12 outcomes. The source delivered here covers the first sequence only.
