# PLC implementation brief

**Status: planned. No compiled PLC project or tested Structured Text implementation is included yet.** The Python controller is a behavioral reference, not a PLC program and not connected to CODESYS.

## Suggested CODESYS project structure

| Object / future export | Purpose |
| --- | --- |
| `ConveyorSorting.project` | Editable native project; save only after creating and checking it |
| `ConveyorSorting.projectarchive` | Archive with required project dependencies for reproduction |
| `exports/E_CellState.st` | State enumeration matching the reference contract |
| `exports/ST_CellInputs.st` | Symbolic Boolean inputs from the I/O map |
| `exports/ST_CellOutputs.st` | Conveyor, extend, ready and alarm outputs |
| `exports/FB_ConveyorSorter.st` | Sequence, fault latch, counters and timers |
| `exports/PLC_PRG.st` | Calls the controller once per cyclic task |
| `exports/PRG_TestSequence.st` | Deterministic input sequence for scan/timer tests in simulation only |

These are proposed deliverables, not files already present. Keep the native project and a readable text or PLCopen XML export together after each verified milestone. Record the IDE and library versions.

## Build in this order

1. Create a Standard Project in ST. Use one 20 ms cyclic task and no physical output mapping.
2. Add state and I/O types; initialize state to STOPPED, outputs false and counters zero. Make retention a deliberate later decision; the reference counters reset on a new process.
3. Add independent `R_TRIG` instances for Start and Reset. Call them every scan so a held button cannot become a new edge merely because the state changes.
4. Implement STOPPED/READY startup and FEED/ACCEPT. Initialize movement outputs false each scan, then derive them from the resulting state.
5. Add separate phase timers. Call every timer every scan with its state condition; inactive timers must reset. Use `TON` and explicitly verify elapsed-time behavior at state entry and at the deadline.
6. Add EXTEND/RETRACT and remember reject passage across both phases. Count only when full passage and return home are complete.
7. Apply the fault and stop priorities in [control design](../docs/control-design.md). Do not let a general Stop branch erase a latched fault.
8. Replay the [test matrix](../docs/test-plan.md), then add the operator display.

Keep the test-sequence program behind an unmistakable simulation-only selection. Do not implement a connection to Python as part of the first port. Manually or deterministically replay the same input sequences in each environment and compare results.

## First PLC exercise

Implement only STOPPED → READY → FEED → ACCEPT → READY. Force the station and accept photoeye in the documented order. Demonstrate that holding the accept sensor high produces no count and eventually times out. Then release it before timeout and confirm exactly one count. Explain which rung/ST condition prevents counting twice.

## Port completion gate

Record zero compilation errors, the task configuration, actual results for R01–R12, a normal cycle and an interrupted-cycle recovery. The portable reference model passing does not satisfy this gate on its own.
