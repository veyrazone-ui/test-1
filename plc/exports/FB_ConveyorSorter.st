FUNCTION_BLOCK FB_ConveyorSorter
VAR_INPUT
    i : ST_CellInputs;
END_VAR
VAR_OUTPUT
    o : ST_CellOutputs;
    state : E_CellState := E_CellState.STOPPED;
    fault : E_CellFault := E_CellFault.NONE;
    accepted_count : UDINT := 0;
    rejected_count : UDINT := 0; (* Reserved; never incremented in Stage 2. *)
    accepted_seen : BOOL := FALSE;
    start_edge : BOOL;
    reset_edge : BOOL;
    feed_et : TIME;
    accept_et : TIME;
    feed_q : BOOL;
    accept_q : BOOL;
END_VAR
VAR
    startTrigger : R_TRIG;
    resetTrigger : R_TRIG;
    feedTimer : TON;
    acceptTimer : TON;
    scanState : E_CellState;
    clearPath : BOOL;
END_VAR
VAR CONSTANT
    FEED_TIMEOUT : TIME := T#5s;
    ACCEPT_TIMEOUT : TIME := T#3s;
END_VAR

(* IMPLEMENTATION: paste below this line into the ST implementation pane. *)
(* Simulation-only, one call per 20 ms task. No RETAIN or physical addresses. *)
scanState := state;
startTrigger(CLK := i.start);
resetTrigger(CLK := i.reset);
start_edge := startTrigger.Q;
reset_edge := resetTrigger.Q;
clearPath := NOT (i.station OR i.accepted OR i.rejected)
             AND i.pusher_home AND NOT i.pusher_extended;

(* Preserve the first fault. Global checks precede Stop and normal sequence. *)
IF state <> E_CellState.FAULT THEN
    IF NOT i.permissive_ok THEN
        fault := E_CellFault.INTERLOCK_OPEN;
    ELSIF i.pusher_home AND i.pusher_extended THEN
        fault := E_CellFault.LIMIT_CONFLICT;
    ELSIF i.accepted AND i.rejected THEN
        fault := E_CellFault.EXIT_CONFLICT;
    ELSIF (state <> E_CellState.STOPPED) AND (state <> E_CellState.READY)
        AND (state <> E_CellState.FEED) AND (state <> E_CellState.ACCEPT) THEN
        fault := E_CellFault.INVALID_STATE;
    END_IF;
    IF fault <> E_CellFault.NONE THEN
        state := E_CellState.FAULT;
    END_IF;
END_IF;

IF state = E_CellState.FAULT THEN
    (* A new fault must remain observable for its detection scan.
       A Reset edge consumed on that scan cannot also recover it. *)
    IF (scanState = E_CellState.FAULT) AND reset_edge AND NOT i.start AND NOT i.stop
        AND i.permissive_ok AND clearPath THEN
        fault := E_CellFault.NONE;
        state := E_CellState.READY;
    END_IF;
ELSIF i.stop THEN
    state := E_CellState.STOPPED;
ELSE
    CASE state OF
        E_CellState.STOPPED:
            IF reset_edge AND NOT i.start AND clearPath THEN
                state := E_CellState.READY;
            END_IF;
        E_CellState.READY:
            IF start_edge AND NOT i.reset THEN
                IF clearPath THEN
                    state := E_CellState.FEED;
                ELSE
                    fault := E_CellFault.START_NOT_CLEAR;
                    state := E_CellState.FAULT;
                END_IF;
            END_IF;
    END_CASE;
END_IF;

(* Start FEED's TON on the READY -> FEED scan, not one scan later.
   Each TON is called once every scan, including STOPPED/FAULT scans. *)
feedTimer(IN := state = E_CellState.FEED, PT := FEED_TIMEOUT);
IF (scanState = E_CellState.FEED) AND (state = E_CellState.FEED) THEN
    IF feedTimer.Q THEN
        fault := E_CellFault.FEED_TIMEOUT;
        state := E_CellState.FAULT;
    ELSIF NOT i.pusher_home THEN
        fault := E_CellFault.PUSHER_NOT_HOME;
        state := E_CellState.FAULT;
    ELSIF i.accepted OR i.rejected THEN
        fault := E_CellFault.UNEXPECTED_EXIT;
        state := E_CellState.FAULT;
    ELSIF i.station THEN
        IF i.metal THEN
            fault := E_CellFault.METAL_ROUTE_NOT_IMPLEMENTED;
            state := E_CellState.FAULT;
        ELSE
            state := E_CellState.ACCEPT;
        END_IF;
    END_IF;
END_IF;

(* Start ACCEPT's TON on the FEED -> ACCEPT scan. scanState prevents
   evaluating a newly entered phase twice in one scan. *)
acceptTimer(IN := state = E_CellState.ACCEPT, PT := ACCEPT_TIMEOUT);
IF (scanState = E_CellState.ACCEPT) AND (state = E_CellState.ACCEPT) THEN
    IF acceptTimer.Q THEN
        fault := E_CellFault.ACCEPT_TIMEOUT;
        state := E_CellState.FAULT;
    ELSIF NOT i.pusher_home THEN
        fault := E_CellFault.PUSHER_NOT_HOME;
        state := E_CellState.FAULT;
    ELSIF i.rejected THEN
        fault := E_CellFault.UNEXPECTED_EXIT;
        state := E_CellState.FAULT;
    ELSE
        accepted_seen := accepted_seen OR i.accepted;
        IF accepted_seen AND NOT i.accepted AND NOT i.station THEN
            IF accepted_count = UDINT#4294967295 THEN
                fault := E_CellFault.COUNT_OVERFLOW;
                state := E_CellState.FAULT;
            ELSE
                accepted_count := accepted_count + UDINT#1;
                state := E_CellState.READY;
            END_IF;
        END_IF;
    END_IF;
END_IF;

(* Discard incomplete passage memory on completion, Stop or any fault. *)
IF state <> E_CellState.ACCEPT THEN
    accepted_seen := FALSE;
END_IF;
(* Diagnostics show this scan's timer calls; an exited timer resets on
   its next call (next scan). These are not end-state elapsed counters. *)
feed_et := feedTimer.ET;
accept_et := acceptTimer.ET;
feed_q := feedTimer.Q;
accept_q := acceptTimer.Q;

(* Assign every output every scan from the resulting state. *)
o.conveyor := (state = E_CellState.FEED) OR (state = E_CellState.ACCEPT);
o.extend := FALSE;
o.alarm := state = E_CellState.FAULT;
o.ready := (state = E_CellState.READY) AND clearPath;
END_FUNCTION_BLOCK
