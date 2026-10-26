# Optional CAD-to-CAM extension

**Status: planned, simulation only. No G-code or machine-ready program is included.** Keep this optional until PLC behavior, tests and CAD deliverables are complete.

Use the sensor mounting plate from `cad/` as the manufacturing example. In FreeCAD CAM, create a job and document the selected stock, work coordinate origin, fixture/clamp envelope and proposed tools. An initial operation sequence could include facing, mounting slots, sensor feature and profile; choose it based on the final plate and workholding.

Record these decisions rather than filling them with assumed machine facts:

| Decision | Evidence needed |
| --- | --- |
| Material and stock dimensions | Actual selected plate design plus machining allowance |
| Workholding | Sketch showing retained material, support and clamp clearance throughout operations |
| Tools and cutting data | Selected tool geometry and manufacturer/material guidance |
| Origin and safe heights | Setup diagram with units, axes, stock top and clearance |
| Operation order | Reason the part remains securely held during machining |
| Postprocessor | Selected machine/control compatibility, only if a real machine is identified |

Run toolpath simulation and inspect stock removal, collisions/warnings, unmachined areas and tool access. Capture the simulated result and list what the simulator does not prove. If no real machine is selected, stop at the CAM setup and simulation; do not claim machine-ready G-code. Any later machining needs machine-specific review and supervised setup.

This extension demonstrates manufacturability thinking connected to the automation cell; it is not evidence of having operated a CNC machine.
