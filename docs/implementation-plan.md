# Staged implementation plan

The repository contains a working reference scaffold. The learning work below remains to be carried out and evidenced. Suggested effort is about 40 hours spread over eight weeks; it is an estimate, not a commitment or a claim about progress. Keep the core deliverable ahead of optional CNC work.

| Stage | Effort | Work to do | Learning outcome | Gate and evidence |
| --- | --- | --- | --- | --- |
| 1 — Understand and reproduce | 4 h | Run the tests and demos. Trace one metal and one non-metal part by hand. Explain every I/O bit. Change the feed timeout on a branch and add/update a boundary test. | Read a scan-based program; translate process behavior into testable requirements. | Record Python version, test log and an explanation of the timer change. Restore or justify the chosen setting. |
| 2 — First PLC sequence | 6 h | Set up a CODESYS V3 Standard Project and 20 ms cyclic task. Create state and I/O types. Implement STOPPED, READY, FEED and ACCEPT using ST, Start/Reset edge detectors and per-state timers. | Use PLC scan execution, edge detection, timers and symbolic I/O. | Zero compile errors; Reset never moves outputs; one non-metal cycle counts only after passage. Save project and text export. |
| 3 — Reject and fault handling | 6 h | Implement EXTEND/RETRACT with feedback. Add all fault codes and recovery rules. Test loss of permissive and Stop in each active state. | Design interlocks, latched diagnostics and a deliberate recovery sequence. | Metal cycle counts once. Missing limit feedback times out. Stop/reset/start behavior matches the requirements. |
| 4 — Verify against requirements | 6 h | Replay the test matrix in CODESYS. Test a deadline arrival and a scan-before-deadline arrival. Repeat mixed cycles. Compare state, outputs and counts to the reference traces. | Distinguish reference testing from PLC verification; investigate timing differences. | Record actual outcomes for every required PLC test. Any discrepancy has a fix or explicit accepted limitation. |
| 5 — Operator interface | 4 h | Build the HMI brief using a watch list first, then a compact IDE visualization if available. Separate operator controls from simulated sensor controls. | Communicate state, faults and recovery clearly to an operator. | Show Start/Stop/Reset, state, counters and fault reason; demonstrate recovery without directly writing the state variable. |
| 6 — Mechanical design | 6 h | Model the cell envelope and sensor mounting plate in FreeCAD. Calculate travel and clearance. Export editable CAD, STEP and a dimensioned drawing. | Connect control assumptions to geometry and manufacturing constraints. | No interference in the proposed pusher envelope; sufficient sensor adjustment; units and datums present; timing assumptions updated if geometry changes. |
| 7 — Optional CNC extension | 4 h | Create a CAM setup for the mounting plate. Document stock, origin, workholding and operations; simulate. If time is short, add a PLC sensor-debounce investigation instead. | Relate a functional component to manufacturability, or study signal conditioning. | Toolpath simulation reviewed for clearance and residual material, with screenshots; no claim of machining. Alternative: tested debounce change and timing impact note. |
| 8 — Portfolio release | 4 h | Record a 60–90 s walkthrough; write a short engineering reflection; complete the evidence table and check README status against actual work. | Explain decisions, verification and limitations to an engineering reviewer. | Links to code, PLC exports, actual results, CAD and demo work from a fresh checkout. Tag a release only when the MVP gates are met. |

## Branch-sized tasks

Suggested branch names are examples; they have not been created or assigned:

- `feat/plc-core`: PLC types, task setup and accept route.
- `feat/plc-reject-faults`: reject route, faults and controlled recovery.
- `test/plc-acceptance`: recorded PLC test matrix and trace comparison.
- `feat/operator-display`: HMI plus a short fault/recovery recording.
- `design/sensor-mount`: editable CAD, neutral export and dimensioned drawing.
- `docs/portfolio-demo`: final evidence links, limitations and reflection.

Each change should state what behavior it changes and which tests or design checks demonstrate it. Use small commits so a reviewer can follow the development, including mistakes and fixes that taught something.

## Demonstration outline

1. Explain the process and the one-part assumption in 10 seconds.
2. Run one accept and one reject cycle; show the counters.
3. Inject a missing-feedback fault; show outputs off and a useful fault message.
4. Restore the input; show that recovery still requires Reset and a fresh Start.
5. Show the sensor mounting plate and its relationship to the sensor position.
6. Finish with what was verified in software and what still needs hardware validation.

Only describe personal contributions or mastered skills after being able to explain and reproduce them. This starter can support learning, but using it alone is not evidence of completed PLC, CAD or CNC work.
