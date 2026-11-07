PROGRAM PRG_TestSequence
VAR
    (* Set testCase while stopped after an IDE Reset Cold; then Run.
       0 normal + held Start + Stop/Reset/fresh Start; 1 FEED deadline;
       2 ACCEPT deadline; 3 FEED one scan early; 4 ACCEPT one scan early;
       5 reserved EXTEND + Reset; 6 reserved RETRACT + Reset. *)
    testCase : UINT := 0;
    scan : UINT := 0;
    done : BOOL := FALSE;
    sequence_passed : BOOL := FALSE; (* Assertions only, NOT a measured timing PASS. *)
    failed : BOOL := FALSE;
    inputs : ST_CellInputs;
    dut : FB_ConveyorSorter;
    samples : ARRAY[0..300] OF ST_Stage2Sample;
END_VAR

(* IMPLEMENTATION: paste below this line into the ST implementation pane. *)
(* Simulation-only alternative task entry. Never schedule alongside PLC_PRG.
   Boundary cases use nominal scan counts. External timestamped task traces
   are mandatory for timing verdicts; this array has no measured clock. *)
IF NOT done THEN
    inputs.start := scan >= 2;
    inputs.reset := scan = 1;
    inputs.stop := FALSE;
    inputs.permissive_ok := TRUE;
    inputs.station := FALSE;
    inputs.metal := FALSE;
    inputs.accepted := FALSE;
    inputs.rejected := FALSE;
    inputs.pusher_home := TRUE;
    inputs.pusher_extended := FALSE;
    CASE testCase OF
        0:
            inputs.station := (scan >= 3) AND (scan <= 5);
            inputs.accepted := (scan = 4) OR (scan = 5);
            IF scan >= 9 THEN inputs.start := scan >= 12; END_IF;
            inputs.stop := scan = 9;
            inputs.reset := (scan = 1) OR (scan = 10);
        1:
            inputs.station := scan = 252;
        2:
            inputs.station := scan = 3;
            inputs.accepted := (scan >= 4) AND (scan < 153);
        3:
            inputs.station := scan = 251;
            inputs.accepted := scan = 252;
        4:
            inputs.station := scan = 3;
            inputs.accepted := (scan >= 4) AND (scan < 152);
        5, 6:
            inputs.start := FALSE;
            inputs.reset := (scan = 1) OR (scan = 2) OR (scan = 4);
            (* Deliberate test-only state injection before the detection call.
               Never copy this assignment into PLC_PRG or the controller FB. *)
            IF scan = 1 THEN
                IF testCase = 5 THEN
                    dut.state := E_CellState.EXTEND;
                ELSE
                    dut.state := E_CellState.RETRACT;
                END_IF;
            END_IF;
    ELSE
        failed := TRUE;
        done := TRUE;
    END_CASE;

    IF NOT done THEN
        samples[scan].entry_state := dut.state;
        dut(i := inputs);
        samples[scan].scan := scan;
        samples[scan].inputs := inputs;
        samples[scan].state := dut.state;
        samples[scan].fault := dut.fault;
        samples[scan].outputs := dut.o;
        samples[scan].accepted_count := dut.accepted_count;
        samples[scan].accepted_seen := dut.accepted_seen;
        samples[scan].feed_et := dut.feed_et;
        samples[scan].accept_et := dut.accept_et;
        samples[scan].feed_q := dut.feed_q;
        samples[scan].accept_q := dut.accept_q;

        failed := failed OR dut.o.extend OR (dut.accepted_count > 1)
                  OR (dut.rejected_count <> 0);
        IF scan = 0 THEN
            failed := failed OR (dut.state <> E_CellState.STOPPED)
                      OR dut.o.conveyor OR (dut.accepted_count <> 0);
        ELSIF (scan = 1) AND (testCase <= 4) THEN
            failed := failed OR (dut.state <> E_CellState.READY) OR dut.o.conveyor;
        ELSIF (scan = 2) AND (testCase <= 4) THEN
            failed := failed OR (dut.state <> E_CellState.FEED)
                      OR NOT dut.o.conveyor OR (dut.feed_et <> T#0ms);
        END_IF;

        CASE testCase OF
            0:
                IF (scan >= 3) AND (scan <= 5) THEN
                    failed := failed OR (dut.state <> E_CellState.ACCEPT)
                              OR (dut.accepted_count <> 0);
                    IF scan = 3 THEN
                        failed := failed OR (dut.accept_et <> T#0ms) OR dut.accept_q;
                    ELSE
                        failed := failed OR (dut.feed_et <> T#0ms) OR dut.feed_q;
                    END_IF;
                ELSIF (scan >= 6) AND (scan <= 8) THEN
                    failed := failed OR (dut.state <> E_CellState.READY)
                              OR (dut.accepted_count <> 1) OR dut.o.conveyor;
                    IF scan >= 7 THEN
                        failed := failed OR (dut.accept_et <> T#0ms) OR dut.accept_q;
                    END_IF;
                ELSIF scan = 9 THEN
                    failed := failed OR (dut.state <> E_CellState.STOPPED)
                              OR dut.o.conveyor OR (dut.accepted_count <> 1);
                ELSIF (scan = 10) OR (scan = 11) THEN
                    failed := failed OR (dut.state <> E_CellState.READY)
                              OR dut.o.conveyor OR (dut.accepted_count <> 1);
                ELSIF scan >= 12 THEN
                    failed := failed OR (dut.state <> E_CellState.FEED)
                              OR NOT dut.o.conveyor OR (dut.accepted_count <> 1)
                              OR dut.feed_q OR (dut.accept_et <> T#0ms) OR dut.accept_q;
                    IF scan = 12 THEN
                        failed := failed OR (dut.feed_et <> T#0ms);
                    END_IF;
                END_IF;
                done := scan = 13;
            1:
                IF (scan >= 2) AND (scan < 252) THEN
                    failed := failed OR (dut.state <> E_CellState.FEED)
                              OR (dut.accepted_count <> 0);
                ELSIF scan = 252 THEN
                    failed := failed OR (samples[251].state <> E_CellState.FEED)
                              OR samples[251].inputs.station OR NOT inputs.station
                              OR (dut.state <> E_CellState.FAULT)
                              OR (dut.fault <> E_CellFault.FEED_TIMEOUT)
                              OR NOT dut.feed_q OR dut.o.conveyor
                              OR (dut.accepted_count <> 0);
                ELSIF scan = 253 THEN
                    failed := failed OR (dut.state <> E_CellState.FAULT)
                              OR (dut.fault <> E_CellFault.FEED_TIMEOUT)
                              OR dut.feed_q OR (dut.feed_et <> T#0ms)
                              OR dut.o.conveyor OR NOT dut.o.alarm
                              OR (dut.accepted_count <> 0);
                    done := TRUE;
                END_IF;
            2:
                IF (scan >= 3) AND (scan < 153) THEN
                    failed := failed OR (dut.state <> E_CellState.ACCEPT)
                              OR (dut.accepted_count <> 0);
                ELSIF scan = 153 THEN
                    failed := failed OR (samples[152].state <> E_CellState.ACCEPT)
                              OR NOT samples[152].inputs.accepted OR inputs.accepted
                              OR (dut.state <> E_CellState.FAULT)
                              OR (dut.fault <> E_CellFault.ACCEPT_TIMEOUT)
                              OR NOT dut.accept_q OR dut.o.conveyor
                              OR (dut.accepted_count <> 0);
                ELSIF scan = 154 THEN
                    failed := failed OR (dut.state <> E_CellState.FAULT)
                              OR (dut.fault <> E_CellFault.ACCEPT_TIMEOUT)
                              OR dut.accept_q OR (dut.accept_et <> T#0ms)
                              OR dut.o.conveyor OR NOT dut.o.alarm
                              OR (dut.accepted_count <> 0);
                    done := TRUE;
                END_IF;
            3:
                IF (scan >= 2) AND (scan < 251) THEN
                    failed := failed OR (dut.state <> E_CellState.FEED)
                              OR (dut.accepted_count <> 0) OR dut.feed_q;
                ELSIF scan = 251 THEN
                    failed := failed OR (samples[250].state <> E_CellState.FEED)
                              OR (samples[250].accepted_count <> 0)
                              OR samples[250].inputs.station OR NOT inputs.station
                              OR (samples[251].entry_state <> E_CellState.FEED)
                              OR (dut.state <> E_CellState.ACCEPT)
                              OR (dut.accepted_count <> 0) OR dut.feed_q
                              OR (dut.feed_et >= T#5s) OR (dut.accept_et <> T#0ms);
                ELSIF scan = 252 THEN
                    failed := failed OR (dut.state <> E_CellState.ACCEPT)
                              OR NOT inputs.accepted OR NOT dut.accepted_seen
                              OR (dut.accepted_count <> 0)
                              OR dut.feed_q OR (dut.feed_et <> T#0ms);
                ELSIF scan = 253 THEN
                    failed := failed OR (samples[252].accepted_count <> 0)
                              OR NOT samples[252].inputs.accepted OR inputs.accepted
                              OR (dut.state <> E_CellState.READY)
                              OR (dut.accepted_count <> 1) OR dut.o.conveyor;
                    done := TRUE;
                END_IF;
            4:
                IF (scan >= 3) AND (scan < 152) THEN
                    failed := failed OR (dut.state <> E_CellState.ACCEPT)
                              OR (dut.accepted_count <> 0) OR dut.accept_q;
                ELSIF scan = 152 THEN
                    failed := failed OR (samples[151].state <> E_CellState.ACCEPT)
                              OR (samples[151].accepted_count <> 0)
                              OR NOT samples[151].accepted_seen
                              OR NOT samples[151].inputs.accepted
                              OR inputs.accepted OR inputs.station
                              OR (samples[152].entry_state <> E_CellState.ACCEPT)
                              OR (dut.state <> E_CellState.READY)
                              OR dut.accept_q OR (dut.accept_et >= T#3s)
                              OR (dut.accepted_count <> 1) OR dut.o.conveyor;
                ELSIF scan = 153 THEN
                    failed := failed OR (dut.state <> E_CellState.READY)
                              OR (dut.accepted_count <> 1) OR dut.o.conveyor
                              OR dut.accept_q OR (dut.accept_et <> T#0ms);
                    done := TRUE;
                END_IF;
            5, 6:
                IF (scan >= 1) AND (scan <= 3) THEN
                    failed := failed OR (dut.state <> E_CellState.FAULT)
                              OR (dut.fault <> E_CellFault.INVALID_STATE)
                              OR NOT dut.o.alarm OR dut.o.ready;
                ELSIF scan >= 4 THEN
                    failed := failed OR (dut.state <> E_CellState.READY)
                              OR (dut.fault <> E_CellFault.NONE)
                              OR dut.o.alarm OR NOT dut.o.ready;
                END_IF;
                failed := failed OR dut.o.conveyor OR (dut.accepted_count <> 0)
                          OR dut.feed_q OR dut.accept_q;
                done := scan = 5;
        END_CASE;
        IF scan = 300 THEN
            failed := TRUE;
            done := TRUE;
        END_IF;
        sequence_passed := done AND NOT failed;
        IF NOT done THEN scan := scan + 1; END_IF;
    END_IF;
END_IF;
(* The runner stops calling its private DUT when done. Timeout modes include
   the following reset-diagnostic scan, but NOT fault recovery. S2-20 requires
   a separate continuous recovery trace. No runtime evidence exists until run. *)
END_PROGRAM
