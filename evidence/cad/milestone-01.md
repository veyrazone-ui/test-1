# CAD milestone 01 — verification record

**Planning complete; CAD execution NOT RUN.** Do not mark pending rows PASS without observing the actual artifacts.

- Design revision/date: A / 2026-11-02
- Repository source baseline: b4ae9c8e9a807e83dc25c779da03d02f277d8354
- Model commit: PENDING
- FreeCAD version/build, OS, geometry kernel: PENDING
- Modeler / checker / execution date: PENDING
- Actual sensor/datasheet revision: UNSELECTED
- Physical validation: NOT PERFORMED
- Assistance: requirements, dimensions and plan prepared with AI assistance. Record modeler's CAD execution separately.

| ID | Acceptance check | Status | Actual observations / evidence |
| --- | --- | --- | --- |
| C01 | I/O and R03–R07/R10 mapped to geometry | DOCUMENTED | cad/sensor-mount-requirements.md |
| C02 | Arithmetic: 6 mm end ligament, 9.5 mm inter-feature ligament, 12.5 mm adjustment, 14411.26 mm³ plate volume | CALCULATED ONLY | cad/freecad-modeling-plan.md; no CAD measurements yet |
| C03 | Native plate opens/recomputes, one solid, sketches fully constrained | NOT RUN | Record solver and geometry results |
| C04 | Native model agrees with dimensions and calculated volume | NOT RUN | Actual dimensions/volume |
| C05 | Thickness 6, slots 20, pitch 48 variants each valid; nominal restored | NOT RUN | Each variant's constraints, geometry and clearances |
| C06 | Both adjustment extremes, washer/nut/service access checked | NOT RUN | Actual distances and wrench-access observations |
| C07 | Selected sensor supports gap, target and first-station sampling | BLOCKED: SENSOR UNSELECTED | Datasheet and sensing-window calculation |
| C08 | Puck/pusher/support/sensor/cable clear at limits and through stroke | NOT RUN | Swept-volume/intermediate checks; distinguish intentional mating contacts |
| C09 | Puck clears belt; chute provides complete reject beam passage | NOT RUN | Extended/downstream poses; remaining dynamics limitations |
| C10 | Native layout relative links work from a different checkout folder | NOT RUN | Fresh-path reopen result |
| C11 | Plate STEP: one solid, correct bounds/features, volume difference ≤0.01% | NOT RUN | Native and imported measurements |
| C12 | Layout STEP object list/count and placements agree | NOT RUN | Declared contents and reimport result |
| C13 | PDF dimensions/notes/datums legible and agree with model | NOT RUN | Actual PDF review |
| C14 | Geometry/timing reconciled, remaining dynamics stated | CALCULATED ONLY | 2.85 s center-datum feed; 2.1 s accept; 0.5 s stroke |
| C15 | Manifest, hashes, revision and README status agree | NOT RUN | Complete artifact-manifest.md |

C07 may remain explicitly unresolved for a conceptual CAD release only if all geometric checks pass and the release clearly says sensor selection/sensing performance unverified. It blocks claims of hardware fit and guaranteed classification. C09 requires a modeled downstream route; unmeasured chute dynamics must remain a stated limitation, not a passed physical timing test.

## Required images

Save actual captures in `evidence/cad/images/`:
1. `01-plate-parameters.png`: aliases and nominal values.
2. `02-plate-constrained.png`: feature tree and zero-DOF sketches (additional captures as needed).
3. `03-plate-isometric.png`: completed component.
4. `04-classification-pose.png`: beam, target leading edge, sensor axis and gap.
5. `05-pusher-home.png` and `06-pusher-extended.png`: dimensions and clearance.
6. `07-adjustment-limits.png`: both extremes and service/cable envelopes.
7. `08-step-reimport.png`: imported solid and measurements.
8. `09-drawing-preview.png`: exported PDF rendered as viewed.
9. `10-reject-departure.png`: puck beyond reject beam.

## Findings

| Date | Check | Actual observation | Correction / decision | Recheck |
| --- | --- | --- | --- | --- |
| PENDING | — | No CAD checks executed | — | — |

## Release wording

Now: "CAD requirements and modeling plan prepared; models, STEP exports and drawing pending."

After conceptual checks: "Parametric models, reopened STEP exports and dimensioned drawing completed and checked against stated geometric assumptions. Sensor selection and physical performance remain unverified."

The checklist alone does not close Stage 6.
