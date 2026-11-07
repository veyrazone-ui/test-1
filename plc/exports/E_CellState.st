{attribute 'qualified_only'}
{attribute 'strict'}
TYPE E_CellState :
(
    STOPPED := 0,
    READY := 1,
    FEED := 2,
    ACCEPT := 3,
    EXTEND := 4,  (* Reserved for Stage 3; invalid in this controller. *)
    RETRACT := 5, (* Reserved for Stage 3; invalid in this controller. *)
    FAULT := 6
) := STOPPED;
END_TYPE
