PROGRAM PRG_TestSequence
VAR
    (* Set testCase while stopped after an IDE Reset Cold; then Run.
       0 normal + held Start + Stop/Reset; 1 FEED deadline;
       2 ACCEPT deadline; 3 FEED one scan early; 4 ACCEPT one scan early. *)
    testCase : UINT := 0;
    scan : UINT := 0;
    done : BOOL := FALSE;
    passed : BOOL := FALSE;
    failed : BOOL := FALSE;
    inputs : ST_CellInputs;
    dut : FB_ConveyorSorter;
    samples : ARRAY[0..300] OF ST_Stage2Sample;
END_VAR

(* IMPLEMENTATION: paste below this line into the ST implementation pane. *)
(* Simulation-only alternative task entry. Never schedule alongside PLC_PRG.
   Boundary cases use nominal scan counts; inspect actual ET/Q for jitter. *)
IF NOT done THEN
    inputs.start := scan >= 2; (* Held across completion until case 0 Stop. *)
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
            IF scan >= 9 THEN inputs.start := FALSE; END_IF;
            inputs.stop := scan = 9;
            inputs.reset := (scan = 1) OR (scan = 10);
        1:
            inputs.station := scan >= 252;
        2:
            inputs.station := scan = 3;
            inputs.accepted := (scan >= 4) AND (scan < 153);
        3:
            inputs.station := scan = 251;
            inputs.accepted := scan = 252;
        4:
            inputs.station := scan = 3;
            inputs.accepted := (scan >= 4) AND (scan < 152);
    ELSE
        failed := TRUE;
        done := TRUE;
    END_CASE;

    IF NOT done THEN
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

        failed := failed OR dut.o.extend OR (dut.accepted_count > 1);
        IF scan = 0 THEN
            failed := failed OR (dut.state <> E_CellState.STOPPED)
                      OR dut.o.conveyor OR (dut.accepted_count <> 0);
        ELSIF scan = 1 THEN
            failed := failed OR (dut.state <> E_CellState.READY) OR dut.o.conveyor;
        ELSIF scan = 2 THEN
            failed := failed OR (dut.state <> E_CellState.FEED)
                      OR NOT dut.o.conveyor OR (dut.feed_et <> T#0ms);
        END_IF;

        CASE testCase OF
            0:
                IF (scan >= 3) AND (scan <= 5) THEN
                    failed := failed OR (dut.state <> E_CellState.ACCEPT)
                              OR (dut.accepted_count <> 0);
                ELSIF (scan >= 6) AND (scan <= 8) THEN
                    failed := failed OR (dut.state <> E_CellState.READY)
                              OR (dut.accepted_count <> 1) OR dut.o.conveyor;
                ELSIF scan = 9 THEN
                    failed := failed OR (dut.state <> E_CellState.STOPPED)
                              OR dut.o.conveyor OR (dut.accepted_count <> 1);
                ELSIF scan >= 10 THEN
                    failed := failed OR (dut.state <> E_CellState.READY)
                              OR dut.o.conveyor OR (dut.accepted_count <> 1);
                END_IF;
                done := scan = 12;
            1:
                IF (scan >= 2) AND (scan < 252) THEN
                    failed := failed OR (dut.state <> E_CellState.FEED);
                ELSIF scan = 252 THEN
                    failed := failed OR (dut.state <> E_CellState.FAULT)
                              OR (dut.fault <> E_CellFault.FEED_TIMEOUT)
                              OR NOT dut.feed_q OR dut.o.conveyor
                              OR (dut.accepted_count <> 0);
                    done := TRUE;
                END_IF;
            2:
                IF (scan >= 3) AND (scan < 153) THEN
                    failed := failed OR (dut.state <> E_CellState.ACCEPT)
                              OR (dut.accepted_count <> 0);
                ELSIF scan = 153 THEN
                    failed := failed OR (dut.state <> E_CellState.FAULT)
                              OR (dut.fault <> E_CellFault.ACCEPT_TIMEOUT)
                              OR NOT dut.accept_q OR dut.o.conveyor
                              OR (dut.accepted_count <> 0);
                    done := TRUE;
                END_IF;
            3:
                IF scan = 251 THEN
                    failed := failed OR (dut.state <> E_CellState.ACCEPT)
                              OR dut.feed_q;
                ELSIF scan = 253 THEN
                    failed := failed OR (dut.state <> E_CellState.READY)
                              OR (dut.accepted_count <> 1) OR dut.o.conveyor;
                    done := TRUE;
                END_IF;
            4:
                IF scan = 152 THEN
                    failed := failed OR (dut.state <> E_CellState.READY)
                              OR dut.accept_q OR (dut.accepted_count <> 1)
                              OR dut.o.conveyor;
                    done := TRUE;
                END_IF;
        END_CASE;
        IF scan = 300 THEN
            failed := TRUE;
            done := TRUE;
        END_IF;
        passed := done AND NOT failed;
        IF NOT done THEN scan := scan + 1; END_IF;
    END_IF;
END_IF;
(* The test stops calling its private DUT when done, preserving samples.
   This is a test runner, not a continuously executing plant controller. *)
END_PROGRAM
