TYPE ST_CellInputs :
STRUCT
    start : BOOL := FALSE;
    reset : BOOL := FALSE;
    stop : BOOL := FALSE;
    permissive_ok : BOOL := TRUE; (* Simulation default, not a safety input. *)
    station : BOOL := FALSE;
    metal : BOOL := FALSE;
    accepted : BOOL := FALSE;
    rejected : BOOL := FALSE;
    pusher_home : BOOL := TRUE;
    pusher_extended : BOOL := FALSE;
END_STRUCT
END_TYPE
