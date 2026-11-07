TYPE ST_Stage2Sample :
STRUCT
    scan : UINT;
    entry_state : E_CellState;
    inputs : ST_CellInputs;
    state : E_CellState;
    fault : E_CellFault;
    outputs : ST_CellOutputs;
    accepted_count : UDINT;
    accepted_seen : BOOL;
    feed_et : TIME;
    accept_et : TIME;
    feed_q : BOOL;
    accept_q : BOOL;
END_STRUCT
END_TYPE
