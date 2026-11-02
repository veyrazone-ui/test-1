# CAD artifact manifest

**All deliverables are pending; none is supplied yet.** Paths are repository-relative. No empty binary placeholders.

| Artifact | Intended path | Revision | Status | SHA-256 |
| --- | --- | --- | --- | --- |
| Editable plate, parameters and TechDraw | cad/models/sensor-mount.FCStd | A | PENDING | PENDING |
| Editable layout | cad/models/conveyor-layout.FCStd | A | PENDING | PENDING |
| Plate neutral solid | cad/exports/sensor-mount.step | A | PENDING | PENDING |
| Nominal layout configuration | cad/exports/conveyor-layout.step | A | PENDING | PENDING |
| Dimensioned drawing | cad/drawings/sensor-mount-rev-A.pdf | A | PENDING | PENDING |

## Export record

- Native source commit: PENDING
- Export date, FreeCAD build, STEP settings: PENDING
- Layout objects included / expected solid count: PENDING
- Native/reimport plate volume and bounds: PENDING
- Relative volume difference: PENDING
- Fresh-checkout link test: PENDING
- Drawing/native revision check: PENDING
- [Verification results](milestone-01.md): NOT RUN

After final saves, compute SHA-256 from repository root, e.g. `sha256sum cad/models/*.FCStd cad/exports/*.step cad/drawings/*.pdf` on Linux or `Get-FileHash` in PowerShell. Paste hashes and commit with actual evidence. Do not hash the manifest into itself.

Screenshots support inspection; they do not replace editable files, STEP exports or drawing.
