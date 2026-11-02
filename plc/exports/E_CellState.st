{attribute 'qualified_only'}
{attribute 'strict'}
TYPE E_CellState :
(
    STOPPED := 0,
    READY := 1,
    FEED := 2,
    ACCEPT := 3,
    EXTEND := 4,  // Reserved for Stage 3; never entered by Stage 2.
    RETRACT := 5, // Reserved for Stage 3; never entered by Stage 2.
    FAULT := 6
) := STOPPED;
END_TYPE
