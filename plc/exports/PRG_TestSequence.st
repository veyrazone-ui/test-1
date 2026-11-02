PROGRAM PRG_TestSequence
VAR
    // SIMULATION ONLY. Configure these initializers OFFLINE, then reset origin.
    // 0 normal + held Start; 1 feed timeout; 2 accept held high;
    // 3 accept never high; 4 station held high; 5 unsupported metal;
    // 6 FEED boundary; 7 ACCEPT boundary.
    uiScenario : UINT := 0;
    uiArrivalScan : UINT := 250; // case 6: 249/250; case 7: 149/150.
    xRun : BOOL := FALSE;       // Write TRUE only after origin reset and trace setup.
    xDone : BOOL := FALSE;
    xFailed : BOOL := FALSE;    // Latched invariant failure, not a full test verdict.
    udiScan : UDINT := 0;
    udiFinishScan : UDINT;
    idleInputs : ST_CellInputs;
    simInputs : ST_CellInputs;
    sorter : FB_ConveyorSorter;
    samples : ARRAY[0..511] OF ST_Stage2Sample;
END_VAR

// IMPLEMENTATION
simInputs := idleInputs;
udiFinishScan := 400;
IF xRun THEN
    // Start before Reset is consumed in STOPPED; then deliberate Reset/Start.
    simInputs.start := (udiScan = 1) OR (udiScan >= 4);
    simInputs.reset := udiScan = 2;
    CASE uiScenario OF
        0:
            simInputs.station := (udiScan >= 10) AND (udiScan <= 17);
            simInputs.accepted := ((udiScan >= 11) AND (udiScan <= 15))
                                  OR (udiScan = 20) OR (udiScan = 21);
            udiFinishScan := 40;
        1:
            // No station detection: wait for FEED timeout.
            simInputs.station := FALSE;
        2:
            simInputs.station := udiScan = 10;
            simInputs.accepted := udiScan >= 11;
        3:
            simInputs.station := udiScan = 10;
        4:
            simInputs.station := udiScan >= 10;
            simInputs.accepted := (udiScan >= 11) AND (udiScan <= 15);
        5:
            simInputs.station := udiScan = 10;
            simInputs.metal := udiScan = 10;
            udiFinishScan := 30;
        6:
            simInputs.station := udiScan = (4 + uiArrivalScan);
            udiFinishScan := 4 + uiArrivalScan + 2;
        7:
            simInputs.station := udiScan = 10;
            simInputs.accepted := (udiScan >= 11) AND (udiScan < (10 + uiArrivalScan));
            udiFinishScan := 10 + uiArrivalScan + 2;
        ELSE
            xFailed := TRUE;
            simInputs.stop := TRUE;
            udiFinishScan := 0;
    END_CASE;
END_IF;
IF xDone THEN
    simInputs.stop := TRUE; // Freeze evidence, then stop on the following scan.
END_IF;

// This program owns its own controller. Do NOT also schedule PLC_PRG.
sorter(i := simInputs);

IF xRun AND NOT xDone THEN
    // Invariants evaluated on the actual controller instance, never a Python port.
    IF sorter.o.extend OR (sorter.udiAcceptedCount > 1) THEN
        xFailed := TRUE;
    END_IF;
    IF sorter.o.conveyor <> ((sorter.eState = E_CellState.FEED)
                             OR (sorter.eState = E_CellState.ACCEPT)) THEN
        xFailed := TRUE;
    END_IF;
    IF (udiScan <= 3) AND sorter.o.conveyor THEN
        xFailed := TRUE;
    END_IF;
    IF uiScenario = 0 THEN
        IF (udiScan < 18) AND (sorter.udiAcceptedCount <> 0) THEN
            xFailed := TRUE;
        END_IF;
        IF (udiScan >= 18) AND ((sorter.udiAcceptedCount <> 1)
                               OR (sorter.eState <> E_CellState.READY)) THEN
            xFailed := TRUE;
        END_IF;
    END_IF;
    IF udiScan <= 511 THEN
        samples[udiScan].scan := udiScan;
        samples[udiScan].inputs := simInputs;
        samples[udiScan].outputs := sorter.o;
        samples[udiScan].state := sorter.eState;
        samples[udiScan].fault := sorter.eFault;
        samples[udiScan].count := sorter.udiAcceptedCount;
        samples[udiScan].acceptedSeen := sorter.xAcceptedSeen;
        samples[udiScan].startEdge := sorter.xStartEdge;
        samples[udiScan].resetEdge := sorter.xResetEdge;
        samples[udiScan].feedDeadline := sorter.xFeedDeadline;
        samples[udiScan].acceptDeadline := sorter.xAcceptDeadline;
        samples[udiScan].feedDecisionET := sorter.tFeedDecisionElapsed;
        samples[udiScan].acceptDecisionET := sorter.tAcceptDecisionElapsed;
        samples[udiScan].feedET := sorter.tFeedElapsed;
        samples[udiScan].acceptET := sorter.tAcceptElapsed;
    ELSE
        xFailed := TRUE;
    END_IF;
    IF udiScan >= udiFinishScan THEN
        xDone := TRUE;
    ELSE
        udiScan := udiScan + 1;
    END_IF;
END_IF;
END_PROGRAM
