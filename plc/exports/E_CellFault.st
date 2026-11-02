{attribute 'qualified_only'}
{attribute 'strict'}
TYPE E_CellFault :
(
    NONE := 0,
    INTERLOCK_OPEN := 1,
    LIMIT_CONFLICT := 2,
    EXIT_CONFLICT := 3,
    START_NOT_CLEAR := 4,
    PUSHER_NOT_HOME := 5,
    UNEXPECTED_EXIT := 6,
    FEED_TIMEOUT := 7,
    ACCEPT_TIMEOUT := 8,
    METAL_ROUTE_NOT_IMPLEMENTED := 9,
    INVALID_STATE := 10
) := NONE;
END_TYPE
