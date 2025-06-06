def raw_repl_set_var(board, var: str, data: bytes):
    """
    Sets a variable in the raw REPL UART board to the specified data.

    This function is needed mostly in the case where the "data" parameter
    is a byte string. Robot framework wants to convert this into a string,
    which causes issues with parsing on the connected board. This function
    guarantees that the data remains in byte string format during the
    transfer.

    The board MUST already be in raw REPL mode before this function is
    used.

    Example usage from Robot (sets board variable "chunk" to the contents
    of robot variable ${this_data}):

        Switch Board to Raw REPL    ${board}
        Raw REPL Set Var    ${board.python_uart.raw_repl}    chunk    ${this_data}
        Switch Board to User REPL    ${board}
    
    :param board: The raw REPL UART board object.
    :param var: The variable name to set.
    :param data: The data to set the variable to, as bytes.
    """
    board.exec("{} = {}".format(var, data))
