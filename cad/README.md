# CAD milestone 01 — sensor mount and cell layout

**Status: requirements, dimensioned modeling plan and evidence structure prepared. Native models, STEP exports and drawing remain pending.** Revision A, 2026-11-02.

1. Read [sensor requirements](sensor-mount-requirements.md).
2. Follow the [FreeCAD modeling plan](freecad-modeling-plan.md).
3. Record actual checks in [CAD evidence](../evidence/cad/milestone-01.md).
4. Complete the [artifact manifest](../evidence/cad/artifact-manifest.md).

## Proposed baseline

| Item | Revision A |
| --- | --- |
| Component | Overhead plate for the `metal` inductive classification sensor |
| Plate | 80 × 40 × 5 mm; assumed 6061-T6 aluminium |
| Frame mounting | Two through slots, 18 overall × 5.5 wide, on 50 mm pitch; assumed M5 fixings |
| Sensor fixing | Ø13 through clearance hole for assumed Ø12 threaded-body sensor and supplier nuts; no plate thread |
| Adjustment | Conservative 12.5 mm total along belt, ±6.25 from nominal |
| Sensor | Ø12 × 50 placeholder, downward-facing, nominal 2 mm above a 10 mm puck |
| Cell | 600 × 80 belt; Ø30 × 10 puck; station x=300; accept beam x=480 |

All dimensions are millimetres. Sensor model, support interface, sensing range and cable are explicit assumptions.

## Artifact locations

| Directory | Intended contents |
| --- | --- |
| `cad/models/` | `sensor-mount.FCStd`, `conveyor-layout.FCStd` |
| `cad/exports/` | `sensor-mount.step`, `conveyor-layout.step` |
| `cad/drawings/` | `sensor-mount-rev-A.pdf`; editable TechDraw page retained in plate model |
| `evidence/cad/` | Checklist, manifest and actual verification results |
| `evidence/cad/images/` | Parameter, sketch, drawing, layout, clearance and reimport screenshots |

Directories currently contain instructions only. Do not create empty CAD files as placeholders.

## Stage 6 gate

Both native models must reopen/recompute, STEP exports must reopen correctly, and the dimensioned drawing must agree with the saved model. Record sensor alignment, adjustment, pusher swept-envelope, service access and timing checks. Geometry completion under labeled assumptions does not prove hardware performance.

Source baseline: `b4ae9c8e9a807e83dc25c779da03d02f277d8354`; [I/O](../docs/io-map.csv), [requirements](../docs/requirements.md), [control design](../docs/control-design.md), [Stage 6](../docs/implementation-plan.md), [optional CAM](../cam/README.md).
