TYPE ST_Stage2Sample :
STRUCT
    scan : UDINT;
    inputs : ST_CellInputs;
    outputs : ST_CellOutputs;
    state : E_CellState;
    fault : E_CellFault;
    count : UDINT;
    acceptedSeen : BOOL;
    startEdge : BOOL;
    resetEdge : BOOL;
    feedDeadline : BOOL;
    acceptDeadline : BOOL;
    feedDecisionET : TIME;
    acceptDecisionET : TIME;
    feedET : TIME;
    acceptET : TIME;
END_STRUCT
END_TYPE
