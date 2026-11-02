PROGRAM PLC_PRG
VAR
    // Write ONLY these inputs when using the manual simulation procedure.
    simInputs : ST_CellInputs;
    sorter : FB_ConveyorSorter;
END_VAR

// IMPLEMENTATION
sorter(i := simInputs);
END_PROGRAM
