# FreeCAD modeling plan — Revision A

**Plan only: CAD execution and exports remain pending.** Units mm. See [requirements](sensor-mount-requirements.md) and [verification record](../evidence/cad/milestone-01.md).

## Master dimensions

Create a Spreadsheet object named `Parameters`; assign aliases to input cells and reference them from sketch dimensions/features, e.g. `Parameters.PlateLength`. Keep model-derived measurements out of input dependencies to prevent circular references.

Local origin: lower-left plate underside. X along length, Y along width, pad +Z.

| Alias / feature | Nominal | Definition |
| --- | ---: | --- |
| PlateLength | 80 | Overall X |
| PlateWidth | 40 | Overall Y |
| PlateThickness | 5 | Pad height |
| MountPitch | 50 | Slot-center separation in X |
| SlotOverall | 18 | End-to-end length, not arc-center spacing |
| SlotWidth | 5.5 | Through-slot width |
| SensorHoleDia | 13 | Through clearance; no tapping |
| SensorX | 40 | Hole center from left end |
| SensorY | 20 | Hole center from lower long edge |
| Slot center X | 15, 65 | PlateLength/2 ± MountPitch/2 |
| Slot center Y | 20 | PlateWidth/2 |
| Slot radius | 2.75 | SlotWidth/2 |
| Arc-center spacing | 12.5 | SlotOverall-SlotWidth |
| Edge break | 0.2–0.5 | Drawing deburr note; not modeled |

Slots run along X. Arc centers: left (8.75,20)/(21.25,20); right (58.75,20)/(71.25,20). Bounds X=6…24 and 56…74, Y=17.25…22.75.

With nominal Ø5 mm bolt shanks, the ideal center travel is 18 − 5 = 13 mm. Use the 12.5 mm between arc centers (±6.25 mm) as the nominal adjustment range. Check usable travel with both fixings, the drawing tolerances and the actual support pitch.

## Editable plate feature sequence

1. Save `cad/models/sensor-mount.FCStd`; record FreeCAD version/build and units.
2. Create `Parameters` and one Part Design Body `SensorMount`.
3. Sketch `PlateOutline` on XY origin plane: rectangle anchored lower-left to origin, horizontal/vertical sides, length/width from aliases. Require zero degrees of freedom.
4. `PlatePad`: pad by PlateThickness.
5. Sketch `MountSlots` on XY origin plane with attachment offset Z=PlateThickness, avoiding a generated-face dependency. Draw two closed obrounds. Use coincidence, tangency, equality, horizontal/vertical and location/size constraints. Fully constrain; do not use blanket fixed geometry to conceal missing dimensions.
6. `MountSlotCut`: Pocket Through all into plate (-Z); inspect preview and reverse direction if necessary.
7. Sketch `SensorBore` on the same offset origin plane. Circle center SensorX/SensorY, diameter SensorHoleDia; fully constrain.
8. `SensorClearanceCut`: Pocket Through all into plate. Final Body must contain one solid with two slots and one round hole.
9. Recompute, save, and use Part Check geometry (BOP check if available). Record errors or clean result. Edge break stays a drawing note.
10. Change/recompute/inspect each variant separately: thickness 5→6→5; slot length 18→20→18; pitch 50→48→50. Record constraint and shape checks, then restore/save nominal. Arbitrary parameter combinations are not guaranteed valid.

A slot length of 20 reduces end ligament to 5 mm. A slot length of 32 with nominal pitch breaks the edge and must be rejected; a geometrically generated solid alone is not a design acceptance.

## Hand checks

These are arithmetic design checks, not CAD inspection results.

| Check | Calculation | Nominal result |
| --- | --- | ---: |
| Slot to short edge | (80-50-18)/2 | 6 mm |
| Slot to long edge | (40-5.5)/2 | 17.25 mm |
| Sensor hole to long edge | 20-13/2 | 13.5 mm |
| Hole-to-slot ligament | 25-18/2-13/2 | 9.5 mm |
| Assumed Ø12 washer to plate end at adjustment extreme | 15-6.25-6 | 2.75 mm |
| Washer to reserved Ø22 nut envelope at closest pose | 25-6.25-6-11 | 1.75 mm |
| One slot area | 5.5×(18-5.5)+π×5.5²/4 | 92.5083 mm² |
| Final volume | [3200-2×92.5083-π×13²/4]×5 | 14411.26 mm³ |

Use the exact formula for volume comparisons. A chosen minimum 5 mm ligament is a concept screening criterion, not a verified strength or fastener standard. The 1.75 mm nut/washer gap does not establish wrench access.

Manufacturing concept: stock with allowance, face if necessary, machine slots, drill/interpolate bore, finish profile, deburr. A 4 mm cutter is a geometric candidate for the 5.5 mm slots; no approved cutting data or workholding is implied. Keep CAM in the [optional study](../cam/README.md).

## Layout model

Save `cad/models/conveyor-layout.FCStd`; use named envelope solids and a layout parameter sheet. Link the editable plate with a relative path; test reopening in a different checkout folder. Do not substitute a mesh for the editable component.

| Object | Proposed envelope / placement |
| --- | --- |
| BeltEnvelope | 600×80×5; top Z=0, Y=-40…40 |
| PuckAtStation | Ø30×10; center X=285,Y=0, bottom Z=0 at first beam interruption |
| StationPhotoeye | Beam X=300,Z=5 across Y; bodies outside belt |
| AcceptPhotoeye | Beam X=480,Z=5 across Y |
| SensorMount | Local origin global (250,-20,25), aligned axes |
| InductiveSensor | Ø12×50, axis X=290,Y=0; tip Z=12, rear Z=62 |
| SensorNuts | Ø22×5 reserves at Z=20…25 and 30…35 |
| CableKeepOut | Ø20×40 above Z=62; replace with real connector/bend geometry |
| BridgeSupport | Crossbars centered X=265/315, 10 wide in X, Z=20…25; supports outside belt |
| PusherFaceHome | X=265…335 (70 wide), Z=0…8, thickness 5 behind contact face Y=-45 |
| PusherFaceExtended | Contact face Y=55, same X/Z; 100 stroke |
| RejectRoute | Toward +Y, chute mouth beyond Y=40; show support of departing puck |
| RejectPhotoeye | Concept beam across X at Y=60,Z=5 |
| LimitFeedback | Separate markers at actuator home/extended positions |
| GuardSpace | Transparent reservation to size after access review; no finished guard design |

Fixings remain at global X=265/315 while plate shifts. Check both adjustment extremes. Plate/support and nut/plate contacts are intentional mating contacts; review all other interference. Include support attachment envelopes in checks; no floating mount may be treated as a completed assembly.

Pusher calculation: face starts Y=-45, 5 mm from belt edge. It travels 30 mm before contacting the centered puck at Y=-15, then moves puck center 70 mm to Y=70. Puck trailing edge ends Y=55: 15 mm clear of belt edge +40. This assumes maintained contact without slip/rotation.

At full extension, puck spans Y=55…85, still blocking the Y=60 reject beam. Its center must move beyond Y=75 for trailing-edge clearance. Show that downstream pose and a chute route that permits it. Verify departure inside the 1 s RETRACT phase once dynamics are known; otherwise change chute, sensor position or timer explicitly.

Check the full pusher sweep. The proposed pusher underside and belt top are both at Z=0, giving **0 mm nominal running clearance**. Resolve the interface and record the minimum clearance over the stroke before passing C08. The face also spans the station beam at X=300, Z=5. Model the finite beam and both housings, then check that the returning pusher and the departing puck clear the beam before a reject count (C09).

Nominal sensor tip/puck clearance is 2 mm and tip/pusher-top clearance is 4 mm. Runout, target variation and deflection consume these gaps. Real stopping distance and pusher X coverage require confirmation.

## Timing reconciliation

Use the proposed 100 mm/s belt speed and 20 ms scan. Under R07, the controller must observe completion strictly before 5 s in FEED, 3 s in ACCEPT and 1 s each in EXTEND and RETRACT. The 0.50 s return estimate covers the cylinder alone. Reject completion also requires the sampled home signal, completed reject passage and a clear station.

| Check | Ideal result | Interpretation |
| --- | --- | --- |
| Original staging estimate | 300/100=3 s | Repository nominal estimate |
| Center at X=0 to first beam interruption | (300-15)/100=2.85 s | Clarifies center datum versus leading-edge event; no timer change proposed |
| Station to accept event | (480-300)/100=1.8 s | Same leading edge at each beam |
| Accept passage complete | (180+30)/100=2.1 s | 0.9 s nominal margin below deadline |
| Photoeye pulse | 30/100=0.30 s | 15 nominal scans |
| Stroke each direction | 100/200=0.50 s | 0.50 s nominal phase margin |
| Inductive-axis geometric lead | 10/100=0.10 s | Actual sensing window still requires verification |

Scripted Python traces do not validate these mechanical calculations. Recalculate after geometry/speed/beam changes; record residual stopping and chute dynamics separately.

## Drawing plan

Create an A4 landscape TechDraw page in `sensor-mount.FCStd`. Top view 1:1, front/side thickness view and small isometric. Use first-angle projection with its symbol.

Reference datums: A underside, B left end (X=0), C lower long edge (Y=0). Labels do not imply geometric tolerances.

Dimension overall 80×40, thickness 5, Ø13 THRU at X=40/Y=20, two slots 18 OVERALL×5.5 THRU with R2.75 ends, centers X=15/65,Y=20. If center locations drive, label 50 pitch REF to avoid duplicate driving dimensions.

Proposed notes (review before manufacture):
- Units mm; material 6061-T6 aluminium, assumed.
- External dimensions and feature locations ±0.2 mm; thickness 5±0.2.
- Sensor hole Ø13 +0.2/0; slot width 5.5 +0.2/0.
- Slot overall 18±0.2; R2.75 REF derives from width.
- Break sharp edges 0.2–0.5; remove burrs; no tapped holes.
- Part CSC-SM-001, revision A, author, date, scale and projection.
- CONCEPT — HARDWARE INTERFACES UNVERIFIED.

These are proposed explicit tolerances, not ISO-class compliance or demonstrated process capability. Export `cad/drawings/sensor-mount-rev-A.pdf`; inspect actual PDF for missing/clipped symbols, overlaps, legibility and agreement with model.

## Export/reopen procedure

Select final plate Body only and export `cad/exports/sensor-mount.step`; exclude intermediate features. Reimport into a fresh document: one solid, 80×40×5 bounds, correct slots/hole, volume within 0.01% of native.

Export `cad/exports/conveyor-layout.step` as one nominal home configuration. Include named physical concept solids; exclude duplicate extended/downstream poses, optical beams and cable/guard keep-outs. Record included objects and expected solid count; verify count and placements on reimport.

STEP does not preserve feature history. Retain both FCStd files and export from the same saved revision as the drawing. Fill the manifest and checksums only after actual generation.

## FreeCAD references

Official project documentation (this mirror is archived; check help matching your installed build for UI differences):

- [Spreadsheet aliases](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Spreadsheet_Workbench.md)
- [Expressions](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Expressions.md)
- [Pocket](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/PartDesign_Pocket.md)
- [Check geometry](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Part_CheckGeometry.md)
- [TechDraw](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/TechDraw_Workbench.md)
