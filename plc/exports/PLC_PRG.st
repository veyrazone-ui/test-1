PROGRAM PLC_PRG
VAR
    simInputs : ST_CellInputs; (* Manual watch-list input image. *)
    sorter : FB_ConveyorSorter;
END_VAR

(* IMPLEMENTATION: paste below this line into the ST implementation pane. *)
sorter(i := simInputs);
END_PROGRAM
