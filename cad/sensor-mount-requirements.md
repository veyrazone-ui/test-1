# Sensor mounting requirements — Revision A

Prepared 2026-11-02 from repository baseline `b4ae9c8e9a807e83dc25c779da03d02f277d8354`.

## Traceability

The [I/O map](../docs/io-map.csv), [requirements](../docs/requirements.md) and [control design](../docs/control-design.md) define the control behavior. The [original CAD brief](https://github.com/veyrazone-ui/test-1/blob/b4ae9c8e9a807e83dc25c779da03d02f277d8354/cad/README.md) proposes the 80 × 40 × 5 mm plate and two adjustable slots. Revision A proposes their 18 × 5.5 mm size, 50 mm pitch and the Ø13 sensor clearance hole.

| ID | Source requirement or design basis | Mechanical requirement | Planned check |
| --- | --- | --- | --- |
| CAD-R01 | `metal` sampled once at first FEED `station` detection (R03) | Inductive reading established before station event; independently position photoeye and inductive sensor | First-detection pose, sensing window and response/filter/scan timing |
| CAD-R02 | Metal selects reject and non-metal selects accept (R03) | Clear target view, controlled sensing gap, no unwanted detection of surrounding metal | Datasheet range, target material and mounting clearances |
| CAD-R03 | Count after `accepted` goes true then false and `station` is clear (R04) | Keep the accept route clear through the exit at X=480 | Show both beam crossings and confirm the station beam is clear at count |
| CAD-R04 | Counting requires prior `pusher_extended` feedback, `pusher_home` on return, completed `rejected` passage (true then false) and `station` clear (R05) | Carry the puck beyond the reject beam and clear the station beam on return | Show full extension, downstream departure and home, including the beam paths |
| CAD-R05 | Conflicting limits or exits, a wrong-route exit, and loss of home feedback during conveyor motion are faults (R10) | Keep `pusher_home` and `pusher_extended` zones distinct, separate the two exit beams and keep the pusher home during FEED/ACCEPT | Review limit positions and which beams each route crosses. Controller tests cover the fault logic. |
| CAD-R06 | `conveyor` in FEED/ACCEPT, `extend` in EXTEND (R06) | Mount and cable clear puck and pusher swept envelope | Limits and intermediate travel checks, with stopping allowance |
| CAD-R07 | FEED, ACCEPT, EXTEND and RETRACT must complete before their deadlines. A completion on the deadline scan faults (R07). | Use common datums and the assumed Ø30 × 10 mm puck, 100 mm/s belt and 20 ms scan to estimate travel | Compare ideal travel and clearance times with each deadline in the [timing plan](freecad-modeling-plan.md#timing-reconciliation). Actual stopping and chute travel remain unmeasured. |
| CAD-R08 | Flat 80×40×5 plate, two adjustable slots in original brief | Parametric, accessible 2.5D part | Constrained sketches, editable model, drawing and STEP checks |

Operator controls, permissive, ready and alarm impose no mounting-hole pattern. The I/O map specifies no sensor catalogue number, electrical polarity, thread, sensing range, support pattern or stopping distance. This plate carries the `metal` sensor only; photoeyes and cylinder switches remain separate layout objects.

## Explicit assumptions and change gates

| Item | Proposed assumption | Required confirmation |
| --- | --- | --- |
| Sensor body | Generic Ø12×50 threaded cylindrical inductive sensor, pointing down | Actual datasheet: thread/length, target, operating range, response and installation restrictions |
| Sensor fixing | Ø13 clearance hole, two supplier nuts; reserve Ø22×5 for each nut | Nut envelopes are placeholders, not a claimed thread/nut standard; verify thread engagement and wrench access |
| Material | 5 mm 6061-T6 aluminium | Stock, stiffness and sensor metal-clearance compatibility |
| Belt/target | Non-metallic belt; centered puck; ferrous steel baseline metal target | Underlying metal bed/fasteners must not trigger sensor; non-ferrous targets require separate checks |
| Sensing gap | Tip z=12; puck top z=10; nominal gap 2 mm | Compare tolerances/runout/deflection with rated operating window; 2 mm is not a proven range |
| Support | Overhead bridge; plate underside z=25; two M5 fixings 50 mm apart along x | Support is a layout envelope; confirm stiffness, pitch, access and real attachment |
| Cable | Ø20 corridor for 40 mm above sensor rear, then outward from motion | Actual connector and cable bend radius |
| Adjustment | ±6.25 mm along x; axial sensor adjustment via nuts | Transverse position fixed to centerline; check lateral puck variation |
| Pusher | Face home y=-45, end y=55; 100 mm stroke | Contact geometry, chute and residual belt movement |

A concept model can retain clearly labeled placeholders. It must not claim real sensor compatibility, strength, sensing performance or hardware readiness.

## Datums and the first station event

Global X is downstream, Y toward reject chute, Z up. Belt top Z=0; belt spans X=0…600, Y=-40…40. X=0 is staging datum. Station beam crosses at X=300, Z=5; accept beam at X=480, Z=5.

Plate local X follows belt, Y follows global Y, Z up. Nominal lower-left-bottom corner is global (250,-20,25). Sensor hole local (40,20) gives global sensor axis (290,0), 10 mm upstream of station.

For an ideal narrow beam, the Ø30 puck center is X=285 when its leading edge first reaches X=300. Placing the inductive sensor at X=300 would put its axis at the target edge. At X=290, the axis is only 5 mm from puck center. This is a geometric candidate, not proof of magnetic detection.

At 100 mm/s, the target leading edge passes that axis 0.10 s before reaching the station beam. One 20 ms scan is 2 mm of travel. Guaranteed detection starts later than first geometric overlap and depends on the sensing field, gap and target. Validate response time, input filtering and scan phase before passing CAD-R01. If insufficient, reposition sensors or formally revise control behavior; do not assume later sampling.

Slot adjustment gives axis X=283.75…296.25, with geometric lead 16.25…3.75 mm (162.5…37.5 ms). Not every mechanically possible position is necessarily a valid sensing position.

## Open decisions

Before physical adaptation, record actual sensor/datasheet revision, thread/nuts/connector, target and gap tolerances, belt/support materials, optical beam dimensions, pusher face/stopping distance, chute departure dynamics and attachment stiffness. FEA is optional only after defensible loads, restraints and allowable deflection exist.
