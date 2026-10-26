# Mechanical design brief

**Status: proposed dimensions; no CAD model, drawing or analysis result is supplied yet.** Use millimetres consistently and label assumed dimensions in the first revision.

## Cell concept

| Item | Starting value / design task |
| --- | --- |
| Belt envelope | 600 mm long × 80 mm wide |
| Part | 30 mm diameter × 10 mm high puck, centered on belt |
| Coordinates | x along belt; y across belt; z vertical; establish a visible datum |
| Classification station | x = 300 mm from staging datum |
| Accept photoeye | x = 480 mm; validate beam position and mounting access |
| Reject action | Pusher moves across belt at classification station into side chute |
| Pusher stroke | Initial 100 mm assumption; verify actual face start position, contact and clearance |
| Guarding envelope | Reserve space around belt and pusher; not a finished guard design |

Show the part and pusher at home and extended positions. A 100 mm stroke is not by itself proof of clearance: the final part position depends on the pusher face's starting location and contact point. Check that the part fully clears the belt and enters the chute. Consider residual belt motion when discussing why the simulation stops instantaneously but a real system may not.

## Manufacturable sensor mounting plate

Make a small plate from the same cell the CAD/CAM study component. Begin with a flat 80 × 40 × 5 mm plate; use two adjustable mounting slots and a sensor mounting feature. Pick the actual slot size, sensor hole and edge clearances after selecting a sensor envelope. Do not call a hole "M12" unless its thread or clearance intent and chosen sensor match.

Parameterize plate length, width, thickness, mounting pitch, slot length and sensor feature location. Add sufficient edge material, tool access and cable/connector clearance. A flat part keeps the optional manufacturing exercise to 2.5D operations.

## Deliverables and checks

- Editable `conveyor-layout.FCStd` and `sensor-mount.FCStd` models.
- STEP exports that reopen correctly, plus a dimensioned drawing PDF.
- A view showing the classification sensor, pusher and reject route together.
- A short note on datums, adjustment range, material assumption and manufacturing method.
- Recorded envelope/interference checks at both pusher limits and sensor visibility checks.
- Updated travel/time calculations if sensor positions change.

An FEA study is optional and should start only after a meaningful load and restraint model exists. A colorful stress plot with invented loads is not a completion criterion.
