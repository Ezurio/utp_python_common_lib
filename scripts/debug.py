#!/usr/bin/env python3

"""A simple test script to allow debugging the serial port communication.
"""

import logging
import sys
sys.path.append('../common_lib/libraries')
import discovery

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s", level=logging.DEBUG
)

boards = discovery.get_connected_boards()
if len(boards) > 0:
    board = boards[0]
    board.open_and_init_board()
    board.python_uart.send('import os')
    resp = board.python_uart.send('os.uname()')
    assert 'version' in resp
    logging.info(f'Version: {resp}')
    board.close_ports_and_reset()
