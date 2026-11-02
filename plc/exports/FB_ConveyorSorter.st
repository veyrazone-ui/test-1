FUNCTION_BLOCK FB_ConveyorSorter
VAR_INPUT
    i : ST_CellInputs;
END_VAR
VAR_OUTPUT
    o : ST_CellOutputs;
    eState : E_CellState := E_CellState.STOPPED;
    eFault : E_CellFault := E_CellFault.NONE;
    udiAcceptedCount : UDINT := 0;
    xAcceptedSeen : BOOL := FALSE;
    xStartEdge : BOOL;
    xResetEdge : BOOL;
    xFeedDeadline : BOOL;   // Pre-transition TON.Q, retained for this scan's trace.
    xAcceptDeadline : BOOL;
    tFeedDecisionElapsed : TIME; // ET before transition/reset, for boundary evidence.
    tAcceptDecisionElapsed : TIME;
    tFeedElapsed : TIME;
    tAcceptElapsed : TIME;
END_VAR
VAR CONSTANT
    cFeedTimeout : TIME := T#5s;
    cAcceptTimeout : TIME := T#3s;
END_VAR
VAR
    rtStart : R_TRIG;
    rtReset : R_TRIG;
    tonFeed : TON;
    tonAccept : TON;
    ePreviousState : E_CellState;
    eNewFault : E_CellFault;
    xClear : BOOL;
END_VAR

// IMPLEMENTATION (paste the code below into the POU implementation pane).
// Simulation-only Stage 2. Call exactly once per 20 ms task. No RETAIN or I/O addresses.
ePreviousState := eState;
rtStart(CLK := i.start);
rtReset(CLK := i.reset);
xStartEdge := rtStart.Q;
xResetEdge := rtReset.Q;
xClear := NOT (i.station OR i.accepted OR i.rejected)
          AND i.pusher_home AND NOT i.pusher_extended;

// Update both timers before checking completion. A timer is also primed/reset
// below on a state change so its time origin is the state-entry scan.
tonFeed(IN := eState = E_CellState.FEED, PT := cFeedTimeout);
tonAccept(IN := eState = E_CellState.ACCEPT, PT := cAcceptTimeout);
xFeedDeadline := tonFeed.Q;
xAcceptDeadline := tonAccept.Q;
tFeedDecisionElapsed := tonFeed.ET;
tAcceptDecisionElapsed := tonAccept.ET;

o.conveyor := FALSE;
o.extend := FALSE; // Stage 2 never operates the pusher.
o.ready := FALSE;
o.alarm := FALSE;
eNewFault := E_CellFault.NONE;

// Global input faults precede Stop and normal transitions. First fault is kept.
IF eState <> E_CellState.FAULT THEN
    IF NOT i.permissive_ok THEN
        eNewFault := E_CellFault.INTERLOCK_OPEN;
    ELSIF i.pusher_home AND i.pusher_extended THEN
        eNewFault := E_CellFault.LIMIT_CONFLICT;
    ELSIF i.accepted AND i.rejected THEN
        eNewFault := E_CellFault.EXIT_CONFLICT;
    END_IF;
END_IF;
IF eNewFault <> E_CellFault.NONE THEN
    eFault := eNewFault;
    eState := E_CellState.FAULT;
END_IF;

IF eState = E_CellState.FAULT THEN
    IF xResetEdge AND NOT i.start AND NOT i.stop AND i.permissive_ok AND xClear THEN
        eFault := E_CellFault.NONE;
        eState := E_CellState.READY;
    END_IF;
ELSIF i.stop THEN
    eState := E_CellState.STOPPED;
ELSE
    CASE eState OF
        E_CellState.STOPPED:
            IF xResetEdge AND NOT i.start AND xClear THEN
                eState := E_CellState.READY;
            END_IF;
        E_CellState.READY:
            // Reset held/pressed together with Start cannot initiate motion.
            // The Start edge is still consumed and must be released/re-pressed.
            IF xStartEdge AND NOT i.reset THEN
                IF xClear THEN
                    eState := E_CellState.FEED;
                ELSE
                    eNewFault := E_CellFault.START_NOT_CLEAR;
                END_IF;
            END_IF;
        E_CellState.FEED:
            IF xFeedDeadline THEN
                eNewFault := E_CellFault.FEED_TIMEOUT;
            ELSIF NOT i.pusher_home THEN
                eNewFault := E_CellFault.PUSHER_NOT_HOME;
            ELSIF i.accepted OR i.rejected THEN
                eNewFault := E_CellFault.UNEXPECTED_EXIT;
            ELSIF i.station THEN
                IF i.metal THEN
                    eNewFault := E_CellFault.METAL_ROUTE_NOT_IMPLEMENTED;
                ELSE
                    eState := E_CellState.ACCEPT;
                END_IF;
            END_IF;
        E_CellState.ACCEPT:
            IF xAcceptDeadline THEN
                eNewFault := E_CellFault.ACCEPT_TIMEOUT;
            ELSIF NOT i.pusher_home THEN
                eNewFault := E_CellFault.PUSHER_NOT_HOME;
            ELSIF i.rejected THEN
                eNewFault := E_CellFault.UNEXPECTED_EXIT;
            ELSE
                xAcceptedSeen := xAcceptedSeen OR i.accepted;
                IF xAcceptedSeen AND NOT i.accepted AND NOT i.station THEN
                    udiAcceptedCount := udiAcceptedCount + 1;
                    eState := E_CellState.READY;
                END_IF;
            END_IF;
        ELSE
            eNewFault := E_CellFault.INVALID_STATE;
    END_CASE;
    IF eNewFault <> E_CellFault.NONE THEN
        eFault := eNewFault;
        eState := E_CellState.FAULT;
    END_IF;
END_IF;

IF eState <> ePreviousState THEN
    // Intentional second invocation on transitions ONLY:
    // reset the departing TON and start the arriving TON in this same scan.
    tonFeed(IN := eState = E_CellState.FEED, PT := cFeedTimeout);
    tonAccept(IN := eState = E_CellState.ACCEPT, PT := cAcceptTimeout);
    xAcceptedSeen := FALSE;
END_IF;
tFeedElapsed := tonFeed.ET;
tAcceptElapsed := tonAccept.ET;
o.conveyor := (eState = E_CellState.FEED) OR (eState = E_CellState.ACCEPT);
o.alarm := eState = E_CellState.FAULT;
o.ready := (eState = E_CellState.READY) AND xClear;
END_FUNCTION_BLOCK
