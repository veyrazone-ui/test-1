# Operator display brief

**Status: planned.** Start with a CODESYS watch list. Add a small IDE visualization after the controller behavior is verified.

| Area | Required content | Behavior to check |
| --- | --- | --- |
| Header | Project name and prominent SIMULATION label | Viewers can identify this as a simulated cell |
| Process | Conveyor, station, accept exit, pusher and reject chute | Show actual command/status variables; do not invent motion feedback |
| Operator controls | Momentary Start, Stop and Reset | Release buttons correctly; Reset never starts a cycle |
| State | STOPPED/READY/FEED/ACCEPT/EXTEND/RETRACT/FAULT | Same state names as the controller and traces |
| Diagnostics | First fault code, plain-language cause to investigate, recovery steps | Existing fault remains visible until eligible reset |
| Counts | Accepted, rejected and total completed | Total equals accepted + rejected; interrupted part is not counted |
| Timing | Current phase elapsed time and configured timeout | Clearly distinguish logical/simulated time from measured hardware time |
| Simulation panel | Sensor toggles, cylinder feedback and permissive status | Separate panel; no direct edits to state or counters to make a test pass |

Use labels as well as color. Disable or explain unavailable actions, but keep controller interlocks authoritative; a disabled screen button is not a substitute for logic checks.

Acceptance demonstration: complete both routes, hold an exit sensor to create a timeout, show the first fault and recovery instruction, clear inputs, reset, and restart with a separate Start press. Store a screenshot or short clip only after this works.
