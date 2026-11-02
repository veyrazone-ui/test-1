# Stage 2 PLC source package

**Status: authored Structured Text and simulation procedure supplied. CODESYS
compilation and execution NOT VERIFIED; Stage 2 gate OPEN.** There is no native
`.project`, `.projectarchive`, compiled PLC application or measured PLC trace yet.
The 27 reference tests exercise Python, not this ST implementation.

## Start here

1. Read [design and state/fault mapping](stage2-mapping.md) and the
   [symbol-to-watch-path I/O map](stage2-io-map.csv).
2. Follow [CODESYS project setup, manual tests and scripted replay](stage2-simulation.md).
3. Record actual results in [the Stage 2 evidence register](../evidence/stage2/README.md)
   and [results.csv](../evidence/stage2/stage2-results.csv). All PLC cases initially say NOT RUN.

## Supplied files

| File | CODESYS object / purpose |
| --- | --- |
| [E_CellState.st](exports/E_CellState.st) | DUT enum; STOPPED, READY, FEED, ACCEPT, FAULT; EXTEND/RETRACT reserved |
| [E_CellFault.st](exports/E_CellFault.st) | DUT enum; supporting guards and explicit unsupported-metal diagnostic |
| [ST_CellInputs.st](exports/ST_CellInputs.st) | DUT structure; all ten reference input symbols and simulation defaults |
| [ST_CellOutputs.st](exports/ST_CellOutputs.st) | DUT structure; four output commands/status bits |
| [FB_ConveyorSorter.st](exports/FB_ConveyorSorter.st) | FB; edge detectors, two TONs, sequence and confirmed count |
| [PLC_PRG.st](exports/PLC_PRG.st) | Manual test PROGRAM; editable simulation inputs and one controller call |
| [ST_Stage2Sample.st](exports/ST_Stage2Sample.st) | DUT structure; per-scan input/state/output/timer/count sample |
| [PRG_TestSequence.st](exports/PRG_TestSequence.st) | Alternative test PROGRAM; five scripted cases and bounded capture array |
| [check_package.py](check_package.py) | Python package consistency checks; no ST compilation or execution |

`exports/` contains readable authored source, not verified IDE-generated exports.
The simulation guide explains how to split declarations and implementation into
the IDE panes. Use one **20 ms cyclic task** and exactly one PROGRAM call. The
Standard library provides TON and R_TRIG; record the resolved version when built.

## Implemented in source

- Startup STOPPED; eligible Reset arms READY without starting movement.
- Start and Reset rising edges sampled every scan; no queued or repeated starts.
- FEED → ACCEPT for non-metal; route sampled at the station.
- Count only after accepted TRUE then FALSE and station clear. Count once, return
  to READY, require a fresh Start for the next part.
- Independent 5 s FEED and 3 s ACCEPT timers, started on state entry; timeout
  evaluated before same-scan completion. Runtime semantics remain to be verified.
- Stop, basic permissive/plausibility guards, first-fault latch and controlled
  recovery; completed count preserved during operator Stop/Reset.
- Explicit metal-route fault; extend output always FALSE, reject count always 0.

READY ignores Start while Reset is asserted, a stricter rule than the current
Python READY branch. Timer ET/Q diagnostics retain the exit scan's values until
the next call. Both differences are explained in [the design](stage2-mapping.md).
The ST count uses UDINT with an overflow fault; Python integers are unbounded.

## Still required

Create/compile/run in CODESYS, resolve any IDE/compiler issues, record actual test
outcomes and timing observations, and save the native project/archive plus IDE
export. Stage 3 reject sequencing and Stage 4 full-cell verification are still
pending. HMI, CAD and CAM retain their existing status. No hardware commissioning,
physical safety function or real-time performance claim is made.

Run local checks from the repository root:

```bash
python -m unittest discover -s tests -v
python plc/check_package.py
```

Passing these commands does **not** pass the Stage 2 PLC gate.
